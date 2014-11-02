# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('openTun')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import sys 
import socket
import time

import openvisualizer.openvisualizer_utils as u
from   openvisualizer.eventBus import eventBusClient

# IPv6 address for TUN interface
IPV6PREFIX = [0xbb,0xbb,0x00,0x00,0x00,0x00,0x00,0x00]
IPV6HOST   = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01]
    
def create():
    '''
    Module-based Factory method to create instance based on operating system
    '''
    # Must import here rather than at top of module to avoid a circular 
    # reference to OpenTun class.
    
    
    if sys.platform.startswith('win32'):
        from openTunWindows import OpenTunWindows
        return OpenTunWindows()
        
    elif sys.platform.startswith('linux'):
        from openTunLinux import OpenTunLinux
        return OpenTunLinux()
        
    elif sys.platform.startswith('darwin'):
        from openTunMACOS import OpenTunMACOS
        return OpenTunMACOS()
        
    else:
        raise NotImplementedError('Platform {0} not supported'.format(sys.platform))

class OpenTun(eventBusClient.eventBusClient):
    '''
    Class which interfaces between a TUN virtual interface and an EventBus.
        
    This class is abstract, with concrete subclases based on operating system.
    '''
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # store params
        
        # register to receive outgoing network packets
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'OpenTun',
            registrations         = [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getNetworkPrefix',
                    'callback'    : self._getNetworkPrefix_notif,
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'v6ToInternet',
                    'callback' : self._v6ToInternet_notif
                },
            ]
        )
        
        # local variables
        self.tunIf                = self._createTunIf()
        if self.tunIf:
            self.tunReadThread    = self._createTunReadThread()
        else:
            self.tunReadThread    = None
        
        # TODO: retrieve network prefix from interface settings
        
        # announce network prefix
        self.dispatch(
            signal        = 'networkPrefix',
            data          = IPV6PREFIX
        )
    
    #======================== public ==========================================
    
    def close(self):
        
        if self.tunReadThread:
            
            self.tunReadThread.close()
            
            # Send a packet to openTun interface to break out of blocking read.
            attempts = 0
            while self.tunReadThread.isAlive() and attempts < 3:
                attempts += 1
                try:
                    log.info('Sending UDP packet to close openTun')
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                    # Destination must route through the TUN host, but not be the host itself.
                    # OK if host does not really exist.
                    dst      = IPV6PREFIX + IPV6HOST
                    dst[15] += 1
                    # Payload and destination port are arbitrary
                    sock.sendto('stop', (u.formatIPv6Addr(dst),18004))
                    # Give thread some time to exit
                    time.sleep(0.05)
                except Exception as err:
                    log.error('Unable to send UDP to close tunReadThread: {0}'.join(err))
    
    #======================== private =========================================
    
    def _v6ToInternet_notif(self,sender,signal,data):
        '''
        Called when receiving data from the EventBus.
        
        This function forwards the data to the the TUN interface.
        Read from tun interface and forward to 6lowPAN
        '''
        raise NotImplementedError('subclass must implement')
    
    def _getNetworkPrefix_notif(self,sender,signal,data):
        return IPV6PREFIX
    
    def _v6ToMesh_notif(self,data):
        '''
        Called when receiving data from the TUN interface.
        
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
        Open a TUN/TAP interface and switch it to TUN mode.
        
        :returns: The handler of the interface, which can be used for later
            read/write operations.
        '''
        raise NotImplementedError('subclass must implement')
        
    def _createTunReadThread(self):
        '''
        Creates the thread to read messages arriving from the TUN interface
        '''
        raise NotImplementedError('subclass must implement')
