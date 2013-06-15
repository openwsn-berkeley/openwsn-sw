import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('eventBusMonitor')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import copy
import json
import socket
import binascii

import openvisualizer_utils as u

from pydispatch import dispatcher
from openTun    import openTun

class eventBusMonitor(object):
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # local variables
        self.dataLock  = threading.Lock()
        self.stats      = {}
        self.socket     = socket.socket(
            socket.AF_INET6,
            socket.SOCK_DGRAM
        )
        self.meshDebugEnabled = False
        
        # give this instance a name
        self.name       = 'eventBusMonitor'
        
        # connect to dispatcher
        dispatcher.connect(
            self._eventBusNotification,
        )
    
    #======================== public ==========================================
    
    def getStats(self):
        
        # get a copy of stats
        with self.dataLock:
            tempStats = copy.deepcopy(self.stats)
        
        # format as a dictionnary
        returnVal = [
            {
                'sender': k[0],
                'signal': k[1],
                'num':    v,
            } for (k,v) in tempStats.items()
        ]
        
        # send back JSON string
        return json.dumps(returnVal)
        
    def setMeshDebugExport(self,isEnabled):
        '''
        Turns on/off the export of a copy of mesh-bound messages to the
        Internet interface, in the form of ZEP packets. Well-suited to
        viewing the packets in Wireshark.
        See http://wiki.wireshark.org/IEEE_802.15.4 for ZEP details.
        '''
        with self.dataLock:
            self.meshDebugEnabled = (True and isEnabled)
        log.info('%s export of ZEP mesh debug packets to Internet',
                'Enabled' if self.meshDebugEnabled else 'Disabled')
    
    #======================== private =========================================
    
    def _eventBusNotification(self,signal,sender,data):
        'Adds the signal to stats log and performs signal-specific handling'
        
        with self.dataLock:
            key = (sender,signal)
            if key not in self.stats:
                self.stats[key] = 0
            self.stats[key] += 1

        if signal=='bytesToMesh' and self.meshDebugEnabled:
            # Forwards a copy of the 6LoWPAN packet destined for the mesh 
            # to the Internet interface for debugging.
            (nextHop,lowpan) = data
            
            zep = self._wrapZepHeaders(lowpan)
            self._dispatchMeshDebugPacket(zep)
            
    def _wrapZepHeaders(self, lowpan):
        '''
        Returns Exegin ZEP protocol header and dummy 802.15.4 header 
        wrapped around outgoing 6LoWPAN layer packet.
        '''
        # IEEE802.15.4                   (data frame with dummy values)
        mac    = [0x41,0xcc]             # frame control
        mac   += [0x66]                  # sequence number
        mac   += [0xff,0xff]             # destination PAN ID
        mac   += [0x01]*8                # destination address
        mac   += [0x02]*8                # source address
        mac   += lowpan
        # CRC
        mac   += u.calculateFCS(mac)
        
        # ZEP
        zep    = [ord('E'),ord('X')]     # Protocol ID String
        zep   += [0x02]                  # Protocol Version
        zep   += [0x01]                  # Type
        zep   += [0x00]                  # Channel ID
        zep   += [0x00,0x01]             # Device ID
        zep   += [0x01]                  # LQI/CRC mode
        zep   += [0xff]
        zep   += [0x01]*8                # timestamp
        zep   += [0x02]*4                # sequence number
        zep   += [0x00]*10               # reserved
        zep   += [21+len(lowpan)+2]      # length
        
        return zep+mac
        
    def _dispatchMeshDebugPacket(self, zep):
        '''
        Wraps ZEP-based debug packet, for outgoing mesh 6LoWPAN message, 
        with UDP and IPv6 headers. Then forwards as an event to the 
        Internet interface.
        '''
        # UDP
        udplen  = len(zep)+8
        
        udp     = [0x00,0x00]                   # src port (unused)
        udp    += [0x45,0x5a]                   # dest port (17754)
        udp    += [udplen >> 8, udplen & 0xff]  # length
        udp    += [0x00,0x00]                   # checksum
        udp    += zep
        
        # Common address for source and destination
        addr    = []
        addr   += openTun.IPV6PREFIX
        addr   += openTun.IPV6HOST
        
        # CRC  See https://tools.ietf.org/html/rfc2460.
      
        #not sure if the payload contains the udp header in this case.
        udp[6:8] = u.calculatePseudoHeaderCRC(addr,addr,[0x00,0x00]+udp[4:6],[0x00,0x00,0x00,17],zep)
        
        
        # IPv6
        ip     = [6<<4]                  # v6 + traffic class (upper nybble)
        ip    += [0x00,0x00,0x00]        # traffic class (lower nybble) + flow label
        ip    += udp[4:6]                # payload length
        ip    += [17]                    # next header (protocol)
        ip    += [8]                     # hop limit (pick a safe value)
        ip    += addr                    # source
        ip    += addr                    # destination
        ip    += udp
        
        dispatcher.send(
                    sender=self.name,
                    signal='v6ToInternet',
                    data  =ip)
