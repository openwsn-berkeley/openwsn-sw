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

class eventBusMonitor(object):
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # local variables
        self.statsLock  = threading.Lock()
        self.stats      = {}
        self.socket     = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )
        
        # give this instance a name
        self.name       = 'eventBusMonitor'
        
        # connect to dispatcher
        dispatcher.connect(
            self._eventBusNotification,
        )
    
    #======================== public ==========================================
    
    def getStats(self):
        
        # get a copy of stats
        with self.statsLock:
            tempStats = copy.deepcopy(self.stats)
        
        # format as a dictionnary
        returnVal = [
            {
                'sender': str(k[0]),
                'signal': str(k[1]),
                'num':    v,
            } for (k,v) in tempStats.items()
        ]
        
        # send back JSON string
        return json.dumps(returnVal)
    
    #======================== private =========================================
    
    def _eventBusNotification(self,signal,sender,data):
        
        if signal=='bytesToMesh':
            
            # ZEP header
            zep  = []
            zep += [ord('E'),ord('X')]     # Protocol ID String
            zep += [0x02]                  # Protocol Version
            zep += [0x01]                  # Type
            zep += [0x00]                  # Channel ID
            zep += [0x00,0x01]             # Device ID
            zep += [0x01]                  # LQI/CRC mode
            zep += [0xff]
            zep += [0x01]*8                # timestamp
            zep += [0x02]*4                # sequence number
            zep += [0x00]*10               # reserved
            zep += [21+len(data)+2]        # length
            
            # IEEE802.15.4
            mac  = []
            mac += [0x41]
            mac += [0xcc]
            mac += [0x66]
            mac += [0xff,0xff]
            mac += [0x01]*8
            mac += [0x02]*8
            
            # 6LoWPAN
            mac += data
            
            # CRC
            mac += u.calculateFCS(mac)
            
            try:
                self.socket.sendto(
                    ''.join([chr(b) for b in zep+mac]),
                    ('10.2.0.77',17754),
                )
            except ValueError as err:
                print err
                print udpPacket
        
        with self.statsLock:
            key = (sender,signal)
            if key not in self.stats:
                self.stats[key] = 0
            self.stats[key] += 1
    