
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('typeCellType')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

import openType

class typeComponent(openType.openType):
    
    COMPONENT_NULL                      = 0x00
    COMPONENT_IDMANAGER                 = 0x01
    COMPONENT_OPENQUEUE                 = 0x02
    COMPONENT_OPENSERIAL                = 0x03
    COMPONENT_PACKETFUNCTIONS           = 0x04
    COMPONENT_RANDOM                    = 0x05
    COMPONENT_RADIO                     = 0x06
    COMPONENT_IEEE802154                = 0x07
    COMPONENT_IEEE802154E               = 0x08
    COMPONENT_RES_TO_IEEE802154E        = 0x09
    COMPONENT_IEEE802154E_TO_RES        = 0x0a
    COMPONENT_RES                       = 0x0b
    COMPONENT_NEIGHBORS                 = 0x0c
    COMPONENT_SCHEDULE                  = 0x0d
    COMPONENT_OPENBRIDGE                = 0x0e
    COMPONENT_IPHC                      = 0x0f
    COMPONENT_FORWARDING                = 0x10
    COMPONENT_ICMPv6                    = 0x11
    COMPONENT_ICMPv6ECHO                = 0x12
    COMPONENT_ICMPv6ROUTER              = 0x13
    COMPONENT_ICMPv6RPL                 = 0x14
    COMPONENT_OPENTCP                   = 0x15
    COMPONENT_OPENUDP                   = 0x16
    COMPONENT_OPENCOAP                  = 0x17
    COMPONENT_TCPECHO                   = 0x18
    COMPONENT_TCPINJECT                 = 0x19
    COMPONENT_TCPPRINT                  = 0x1a
    COMPONENT_UDPECHO                   = 0x1b
    COMPONENT_UDPINJECT                 = 0x1c
    COMPONENT_UDPPRINT                  = 0x1d
    COMPONENT_RSVP                      = 0x1e
    COMPONENT_OHLONE                    = 0x1f
    COMPONENT_HELI                      = 0x20
    COMPONENT_IMU                       = 0x21
    COMPONENT_RLEDS                     = 0x22
    COMPONENT_RREG                      = 0x23
    COMPONENT_RWELLKNOWN                = 0x24
    COMPONENT_RT                        = 0x25
    COMPONENT_REX                       = 0x26
    COMPONENT_RXL1                      = 0x27
    COMPONENT_RINFO                     = 0x28
    COMPONENT_RHELI                     = 0x29
    COMPONENT_RRUBE                     = 0x2a
    COMPONENT_LAYERDEBUG                = 0x2b
    COMPONENT_UDPRAND                   = 0x2c
    
    def __init__(self):
        # log
        log.debug("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        output  = []
        output += [str(self.type)]
        output += [' (']
        output += [self.desc]
        output += [')']
        return ''.join(output)
    
    #======================== public ==========================================
    
    def update(self,type):
        self.type = type
        
        if   type==self.COMPONENT_NULL:
            self.desc = 'NULL'
        elif type==self.COMPONENT_IDMANAGER:
            self.desc = 'IDMANAGER'
        elif type==self.COMPONENT_OPENQUEUE:
            self.desc = 'OPENQUEUE'
        elif type==self.COMPONENT_OPENSERIAL:
            self.desc = 'OPENSERIAL'
        elif type==self.COMPONENT_PACKETFUNCTIONS:
            self.desc = 'PACKETFUNCTIONS'
        elif type==self.COMPONENT_RANDOM:
            self.desc = 'RANDOM'
        elif type==self.COMPONENT_RADIO:
            self.desc = 'RADIO'
        elif type==self.COMPONENT_IEEE802154:
            self.desc = 'IEEE802154'
        elif type==self.COMPONENT_IEEE802154E:
            self.desc = 'IEEE802154E'
        elif type==self.COMPONENT_RES_TO_IEEE802154E:
            self.desc = 'RES_TO_IEEE802154E'
        elif type==self.COMPONENT_IEEE802154E_TO_RES:
            self.desc = 'IEEE802154E_TO_RES'
        elif type==self.COMPONENT_RES:
            self.desc = 'RES'
        elif type==self.COMPONENT_NEIGHBORS:
            self.desc = 'NEIGHBORS '
        elif type==self.COMPONENT_SCHEDULE:
            self.desc = 'SCHEDULE'
        elif type==self.COMPONENT_OPENBRIDGE:
            self.desc = 'OPENBRIDGE'
        elif type==self.COMPONENT_IPHC:
            self.desc = 'IPHC'
        elif type==self.COMPONENT_FORWARDING:
            self.desc = 'FORWARDING'
        elif type==self.COMPONENT_ICMPv6:
            self.desc = 'ICMPv6'
        elif type==self.COMPONENT_ICMPv6ECHO:
            self.desc = 'ICMPv6ECHO'
        elif type==self.COMPONENT_ICMPv6ROUTER:
            self.desc = 'ICMPv6ROUTER'
        elif type==self.COMPONENT_ICMPv6RPL:
            self.desc = 'ICMPv6RPL'
        elif type==self.COMPONENT_OPENTCP:
            self.desc = 'OPENTCP'
        elif type==self.COMPONENT_OPENUDP:
            self.desc = 'OPENUDP'
        elif type==self.COMPONENT_OPENCOAP:
            self.desc = 'OPENCOAP'
        elif type==self.COMPONENT_TCPECHO:
            self.desc = 'TCPECHO'
        elif type==self.COMPONENT_TCPINJECT:
            self.desc = 'TCPINJECT'
        elif type==self.COMPONENT_TCPPRINT:
            self.desc = 'TCPPRINT'
        elif type==self.COMPONENT_UDPECHO:
            self.desc = 'UDPECHO'
        elif type==self.COMPONENT_UDPINJECT:
            self.desc = 'UDPINJECT'
        elif type==self.COMPONENT_UDPPRINT:
            self.desc = 'UDPPRINT'
        elif type==self.COMPONENT_RSVP:
            self.desc = 'RSVP'
        elif type==self.COMPONENT_OHLONE:
            self.desc = 'OHLONE'
        elif type==self.COMPONENT_HELI:
            self.desc = 'HELI'
        elif type==self.COMPONENT_IMU:
            self.desc = 'IMU'
        elif type==self.COMPONENT_RLEDS:
            self.desc = 'RLEDS'
        elif type==self.COMPONENT_RREG:
            self.desc = 'RREG'
        elif type==self.COMPONENT_RWELLKNOWN:
            self.desc = 'RWELLKNOWN'
        elif type==self.COMPONENT_RT:
            self.desc = 'RT'
        elif type==self.COMPONENT_REX:
            self.desc = 'REX'
        elif type==self.COMPONENT_RXL1:
            self.desc = 'RXL1'
        elif type==self.COMPONENT_RINFO:
            self.desc = 'RINFO'
        elif type==self.COMPONENT_RHELI:
            self.desc = 'RHELI'
        elif type==self.COMPONENT_RRUBE:
            self.desc = 'RRUBE'
        elif type==self.COMPONENT_LAYERDEBUG:
            self.desc = 'LAYERDEBUG'
        elif type==self.COMPONENT_UDPRAND:
            self.desc = 'UDPRAND'
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    