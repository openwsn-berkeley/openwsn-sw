import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('OpenTunLinux')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import time
import os
import socket
import sys
import struct

from fcntl import ioctl


from eventBus import eventBusClient

#============================ defines =========================================

## IPv4 configuration of your TUN interface (represented as a list of integers)
TUN_IPv4_ADDRESS    = [ 10,  2,0,1] ##< The IPv4 address of the TUN interface.
TUN_IPv4_NETWORK    = [ 10,  2,0,0] ##< The IPv4 address of the TUN interface's network.
TUN_IPv4_NETMASK    = [255,255,0,0] ##< The IPv4 netmask of the TUN interface.

IPV6PREFIX   = "BBBB:0000:0000:0000"
IFF_TUN      = 0x0001
TUNSETIFF    = 0x400454ca
 
 

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
        
        p =[]
        
        while self.goOn:
            
            # wait for data
            p =  os.read(self.tunIf,self.ETHERNET_MTU)
          
            
            # convert input from a string to a byte list
            p = [ord(b) for b in p]
            
            # make sure it's an IPv6 packet (starts with 0x6x)
            if (p[0]&0xf0)!=0x60:
               # this is not an IPv6 packet
               continue
            
            # because of the nature of tun for Windows, p contains ETHERNET_MTU
            # bytes. Cut at length of IPv6 packet.
            p = p[:self.IPv6_HEADER_LENGTH+256*p[4]+p[5]]
            
            # call the callback
            self.callback(p)
    
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
       
        self.tunReadThread   = TunReadThread(
            self.tunIf,
            self._v6ToMesh_notif
        )
        
        # TODO: retrieve network prefix from interface settings
        
        # announce network prefix
        self.dispatch(
            signal        = 'networkPrefix',
            data          = self.IPV6PREFIX,
        )
        
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _v6ToInternet_notif(self,sender,signal,data):
        '''
        \brief Called when receiving data from the EventBus.
        
        This function forwards the data to the the TUN interface.
        '''
        
        # convert data to string
        data  = ''.join([chr(b) for b in data])
        
        # write over tuntap interface
        os.write(self.tunIf, data)
    
    def _v6ToMesh_notif(self,data):
        '''
        \brief Called when receiving data from the TUN interface.
        
        This function forwards the data to the the EventBus.
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
        debug.info("opening tun interface")
        f=os.open("/dev/net/tun", os.O_RDWR)
        ifs=ioctl(f,TUNSETIFF,struct.pack("16sH","tun%d",IFF_TUN)) 
        ifname=ifs[:16].strip("\x00")
        
        
        # configure IPv6 address
        debug.info("configuring IPv6 address...")
        v = os.system('ifconfig ' + ifname + ' inet6 add ' + IPV6PREFIX + '::1/64')
        v = os.system('ifconfig ' + ifname + ' inet6 add fe80::1/64')
        v = os.system('ifconfig ' + ifname + ' up')
                
        # set static route
        debug.info("setting up static route...")
        os.system('route -A inet6 add ' + IPV6PREFIX + '::/64 dev ' + ifname)
        
        
        # enable IPv6 forwarding
        debug.info("enabling IPv6 forwarding...")
        os.system('echo 1 > /proc/sys/net/ipv6/conf/all/forwarding')       
        
        return tunIf
    
    #======================== helpers =========================================
    