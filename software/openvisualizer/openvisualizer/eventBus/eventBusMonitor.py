# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('eventBusMonitor')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import copy
import json
import binascii

import openvisualizer.openvisualizer_utils as u

from pydispatch import dispatcher
from openvisualizer.openTun    import openTun

class eventBusMonitor(object):
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # store params
        
        # local variables
        self.dataLock                  = threading.Lock()
        self.stats                     = {}
        self.wiresharkDebugEnabled     = False
        self.dagRootEui64              = [0x00]*8
        self.simMode                   = False
        
        # give this instance a name
        self.name                      = 'eventBusMonitor'
        
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
        
    def setWiresharkDebug(self,isEnabled):
        '''
        Turns on/off the export of a copy of mesh-bound messages to the
        Internet interface, in the form of ZEP packets. Well-suited to
        viewing the packets in Wireshark.
        See http://wiki.wireshark.org/IEEE_802.15.4 for ZEP details.
        '''
        with self.dataLock:
            self.wiresharkDebugEnabled = (True and isEnabled)
        log.info('%s export of ZEP mesh debug packets to Internet',
                'Enabled' if self.wiresharkDebugEnabled else 'Disabled')
    
    #======================== private =========================================
    
    def _eventBusNotification(self,signal,sender,data):
        '''
        Adds the signal to stats log and performs signal-specific handling
        '''
        
        with self.dataLock:
            key = (sender,signal)
            if key not in self.stats:
                self.stats[key] = 0
            self.stats[key] += 1
        
        if signal=='infoDagRoot' and data['isDAGroot']==1:
            self.dagRootEui64 = data['eui64'][:]
        
        if signal=='wirelessTxStart':
            # this signal only exists is simulation mode
            self.simMode = True
        
        if self.wiresharkDebugEnabled:
            
            if self.simMode:
                # simulation mode
                
                if signal=='wirelessTxStart':
                    # Forwards a copy of the packet exchanged between simulated motes
                    # to the tun interface for debugging.
                    
                    (moteId,frame,frequency) = data
                    
                    if log.isEnabledFor(logging.DEBUG):
                        output  = []
                        output += ['']
                        output += ['- moteId:    {0}'.format(moteId)]
                        output += ['- frame:     {0}'.format(u.formatBuf(frame))]
                        output += ['- frequency: {0}'.format(frequency)]
                        output  = '\n'.join(output)
                        log.debug(output)
                        print output # poipoi
                    
                    assert len(frame)>=1+2 # 1 for length byte, 2 for CRC
                    
                    # cut frame in pieces
                    length = frame[0]
                    body   = frame[1:-2]
                    crc    = frame[-2:]
                    
                    # wrap with zep header
                    zep   = self._wrapZepCrc(body,frequency)
                    self._dispatchMeshDebugPacket(zep)
            
            else:
                # non-simulation mode
                
                if signal=='fromMote.data':
                    # Forwards a copy of the data received from a mode
                    # to the Internet interface for debugging.
                    (previousHop,lowpan) = data
                    
                    zep = self._wrapMacAndZep(
                        previousHop  = previousHop,
                        nextHop      = self.dagRootEui64,
                        lowpan       = lowpan,
                    )
                    self._dispatchMeshDebugPacket(zep)

                if signal=='fromMote.sniffedPacket':
                    body      = data[0:-3]
                    crc       = data[-3:-1]
                    frequency = data[-1]

                    # wrap with zep header
                    zep   = self._wrapZepCrc(body,frequency)
                    self._dispatchMeshDebugPacket(zep)
                    
                if signal=='bytesToMesh':
                    # Forwards a copy of the 6LoWPAN packet destined for the mesh 
                    # to the tun interface for debugging.
                    (nextHop,lowpan) = data
                    
                    zep = self._wrapMacAndZep(
                        previousHop  = self.dagRootEui64,
                        nextHop      = nextHop,
                        lowpan       = lowpan,
                    )
                    self._dispatchMeshDebugPacket(zep)
        
        
        
    def _wrapMacAndZep(self, previousHop, nextHop, lowpan):
        '''
        Returns Exegin ZEP protocol header and dummy 802.15.4 header 
        wrapped around outgoing 6LoWPAN layer packet.
        '''
        
        phop   = previousHop[:]
        phop.reverse()
        nhop   = nextHop[:]
        nhop.reverse()
        
        # ZEP
        zep    = [ord('E'),ord('X')]   # Protocol ID String
        zep   += [0x02]                # Protocol Version
        zep   += [0x01]                # Type
        zep   += [0x00]                # Channel ID
        zep   += [0x00,0x01]           # Device ID
        zep   += [0x01]                # LQI/CRC mode
        zep   += [0xff]
        zep   += [0x01]*8              # timestamp
        zep   += [0x02]*4              # sequence number
        zep   += [0x00]*10             # reserved
        zep   += [21+len(lowpan)+2]    # length
        
        # IEEE802.15.4                 (data frame with dummy values)
        mac    = [0x41,0xcc]           # frame control
        mac   += [0x66]                # sequence number
        mac   += [0xfe,0xca]           # destination PAN ID
        mac   += nhop                  # destination address
        mac   += phop                  # source address
        mac   += lowpan
        # CRC
        mac   += u.calculateFCS(mac)
        
        return zep+mac
    
    def _wrapZepCrc(self, body, frequency):
        
        # ZEP header
        zep    = [ord('E'),ord('X')]   # Protocol ID String
        zep   += [0x02]                # Protocol Version
        zep   += [0x01]                # Type
        zep   += [frequency]           # Channel ID
        zep   += [0x00,0x01]           # Device ID
        zep   += [0x01]                # LQI/CRC mode
        zep   += [0xff]
        zep   += [0x01]*8              # timestamp
        zep   += [0x02]*4              # sequence number
        zep   += [0x00]*10             # reserved
        zep   += [len(body)+2]      # length
        
        # mac frame
        mac    = body
        mac   += u.calculateFCS(mac)
        
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
        
        # CRC See https://tools.ietf.org/html/rfc2460.
      
        # not sure if the payload contains the udp header in this case.
        udp[6:8] = u.calculatePseudoHeaderCRC(
            src         = addr,
            dst         = addr,
            length      = [0x00,0x00]+udp[4:6],
            nh          = [0x00,0x00,0x00,17],
            payload     = zep,
        )
        
        # IPv6
        ip     = [6<<4]                  # v6 + traffic class (upper nybble)
        ip    += [0x00,0x00,0x00]        # traffic class (lower nibble) + flow label
        ip    += udp[4:6]                # payload length
        ip    += [17]                    # next header (protocol)
        ip    += [8]                     # hop limit (pick a safe value)
        ip    += addr                    # source
        ip    += addr                    # destination
        ip    += udp
        
        dispatcher.send(
            sender = self.name,
            signal = 'v6ToInternet',
            data   = ip,
        )
