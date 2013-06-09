import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('openTunLinux')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import time
import os
import socket
import sys
import struct
import traceback

import openvisualizer_utils as u
import openTun
from   fcntl     import ioctl
from   eventBus  import eventBusClient

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
    \brief Thread which continously reads input from a TUN interface.
    
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
        self.name                 = 'readThread'
        
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
                log.debug('packet captured on tun interface: {0}'.format(u.formatBuf(p)))
    
                # remove tun ID octets
                p = p[4:]
                
                # make sure it's an IPv6 packet (i.e., starts with 0x6x)
                if (p[0]&0xf0) != 0x60:
                    log.debug('this is not an IPv6 packet')
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

class OpenTunLinux(eventBusClient.eventBusClient):
    '''
    \brief Class which interfaces between a TUN virtual interface and an
        EventBus.
    '''
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # initialize parent class
        
        #======================== 6lowPAN->Internet ===========================
        eventBusClient.eventBusClient.__init__(
            self,
            name             = 'OpenTun',
            registrations =  [
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'v6ToInternet',
                    'callback' : self._v6ToInternet_notif
                }
            ]
        )
        
        # local variables
        self.tunIf           = self._createTunIf()
        
        #======================== Internet->6lowPAN ===========================
        self.tunReadThread   = TunReadThread(
            self.tunIf,
            self._v6ToMesh_notif
        )
        
        # TODO: retrieve network prefix from interface settings
        
        # announce network prefix
        self.dispatch(
            signal        = 'networkPrefix',
            data          = openTun.IPV6PREFIX,
        )
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _v6ToInternet_notif(self,sender,signal,data):
        '''
        \brief Called when receiving data from the EventBus.
        
        This function forwards the data to the the TUN interface.
        Read from tun interface and forward to 6lowPAN
        '''
        
        data = VIRTUALTUNID + data
        
        # convert data to string
        data  = ''.join([chr(b) for b in data])
        
        try:
            # write over tuntap interface
            os.write(self.tunIf, data)
            log.debug("data dispatched to tun correctly {0}, {1}".format(signal,sender))
        except Exception as err:
            print err
            log.error(err)
            raise ValueError('Error writing to TUN, cannot send data from {0}'.format(sender))
    
    def _v6ToMesh_notif(self,data):
        '''
        \brief Called when receiving data from the TUN interface.
        
        This function forwards the data to the the EventBus.
        Read from 6lowPAN and forward to tun interface
        '''
        # dispatch to EventBus
        self.dispatch(
            signal        = 'v6ToMesh',
            data          = data,
        )
    
    def _createTunIf(self):
        '''
        \brief Open a TUN/TAP interface and switch it to TUN mode.
        
        \return The handler of the interface, which can be used for later
            read/write operations.
        '''
        #=====
        log.info("opening tun interface")
        f=os.open("/dev/net/tun", os.O_RDWR)
        ifs=ioctl(f,TUNSETIFF,struct.pack("16sH","tun%d",IFF_TUN)) 
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
        
        return f
    
    #======================== helpers =========================================
    
