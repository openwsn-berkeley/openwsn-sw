# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('openTunLinux')
# Do not set the default null log handlers here. Logging already will have been
# configured, because this class is imported later, on the fly, by OpenTun.

import threading
import time
import os
import sys
import struct
import traceback

import openvisualizer.openvisualizer_utils as u
import openTun
from   fcntl     import ioctl
from   openvisualizer.eventBus  import eventBusClient

#============================ defines =========================================

## IPv4 configuration of your TUN interface (represented as a list of integers)
TUN_IPv4_ADDRESS   = [ 10,  2,0,1] ##< The IPv4 address of the TUN interface.
TUN_IPv4_NETWORK   = [ 10,  2,0,0] ##< The IPv4 address of the TUN interface's network.
TUN_IPv4_NETMASK   = [255,255,0,0] ##< The IPv4 netmask of the TUN interface.

## insert 4 octedts ID tun for compatibility (it'll be discard) 
VIRTUALTUNID = [0x00,0x00,0x86,0xdd]

IFF_TUN            = 0x0001
TUNSETIFF          = 0x400454ca

#============================ helper classes ==================================

class TunReadThread(threading.Thread):
    '''
    Thread which continously reads input from a TUN interface.
    
    When data is received from the interface, it calls a callback configured
    during instantiation.
    '''
    
    ETHERNET_MTU        = 1500
    IPv6_HEADER_LENGTH  = 40
    
    def __init__(self,tunIf,callback):
    
        # store params
        self.tunIf                = tunIf
        self.callback             = callback
        
        # local variables
        self.goOn                 = True
        
        # initialize parent
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'TunReadThread'
        
        # start myself
        self.start()
    
    def run(self):
        try:
            p =[]
            
            while self.goOn:
                
                # wait for data
                p =  os.read(self.tunIf,self.ETHERNET_MTU)
           
                # convert input from a string to a byte list
                p = [ord(b) for b in p]
                
                # debug info
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('packet captured on tun interface: {0}'.format(u.formatBuf(p)))
    
                # remove tun ID octets
                p = p[4:]
                
                # make sure it's an IPv6 packet (i.e., starts with 0x6x)
                if (p[0]&0xf0) != 0x60:
                    log.info('this is not an IPv6 packet')
                    continue
                
                # because of the nature of tun for Windows, p contains ETHERNET_MTU
                # bytes. Cut at length of IPv6 packet.
                p = p[:self.IPv6_HEADER_LENGTH+256*p[4]+p[5]]
                
                # call the callback
                self.callback(p)
        except Exception as err:
            errMsg=u.formatCrashMessage(self.name,err)
            print errMsg
            log.critical(errMsg)
            sys.exit(1)
            
    #======================== public ==========================================
    
    def close(self):
        self.goOn = False
    
    #======================== private =========================================
    
#============================ main class ======================================

class OpenTunLinux(openTun.OpenTun):
    '''
    Class which interfaces between a TUN virtual interface and an EventBus.
    '''
    
    def __init__(self):
        # log
        log.info("create instance")
        
        # initialize parent class
        openTun.OpenTun.__init__(self)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _v6ToInternet_notif(self,sender,signal,data):
        '''
        Called when receiving data from the EventBus.
        
        This function forwards the data to the the TUN interface.
        Read from tun interface and forward to 6lowPAN
        '''
        
        # abort if not tun interface
        if not self.tunIf:
            return
        
        # add tun header
        data  = VIRTUALTUNID + data
        
        # convert data to string
        data  = ''.join([chr(b) for b in data])
        
        try:
            # write over tuntap interface
            os.write(self.tunIf, data)
            if log.isEnabledFor(logging.DEBUG):
                log.debug("data dispatched to tun correctly {0}, {1}".format(signal,sender))
        except Exception as err:
            errMsg=u.formatCriticalMessage(err)
            print errMsg
            log.critical(errMsg)
     
    def _createTunIf(self):
        '''
        Open a TUN/TAP interface and switch it to TUN mode.
        
        :returns: The handler of the interface, which can be used for later
            read/write operations.
        '''
        
        try:
            #=====
            log.info("opening tun interface")
            returnVal=os.open("/dev/net/tun", os.O_RDWR)
            ifs=ioctl(returnVal,TUNSETIFF,struct.pack("16sH","tun%d",IFF_TUN)) 
            ifname=ifs[:16].strip("\x00")
            
            #=====
            log.info("configuring IPv6 address...")
            prefixStr = u.formatIPv6Addr(openTun.IPV6PREFIX)
            hostStr   = u.formatIPv6Addr(openTun.IPV6HOST)
            
            v = os.system('ip tuntap add dev ' + ifname + ' mode tun user root')
            v = os.system('ip link set ' + ifname + ' up')
            v = os.system('ip -6 addr add ' + prefixStr + ':' + hostStr + '/64 dev ' + ifname)
            v = os.system('ip -6 addr add fe80::' + hostStr + '/64 dev ' + ifname)
            
            #=====
            log.info("adding static route route...")
            # added 'metric 1' for router-compatibility constraint 
            # (show ping packet on wireshark but don't send to mote at all)
            os.system('ip -6 route add ' + prefixStr + ':1415:9200::/96 dev ' + ifname + ' metric 1') 
            # trying to set a gateway for this route
            #os.system('ip -6 route add ' + prefixStr + '::/64 via ' + IPv6Prefix + ':' + hostStr + '/64') 
            
            #=====
            log.info("enabling IPv6 forwarding...")
            os.system('echo 1 > /proc/sys/net/ipv6/conf/all/forwarding')
            
            #=====
            print('\ncreated following virtual interface:')
            os.system('ip addr show ' + ifname)
            
            #=====start radvd
            #os.system('radvd start')
        
        except IOError as err:
            # happens when not root
            print 'WARNING: could not created tun interface. Are you root? ({0})'.format(err)
            returnVal = None
        
        return returnVal
         
    def _createTunReadThread(self):
        '''
        Creates and starts the thread to read messages arriving from the
        TUN interface.
        '''
        return TunReadThread(
            self.tunIf,
            self._v6ToMesh_notif
        )
   
    #======================== helpers =========================================
    
