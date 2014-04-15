# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('typeCellType')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import openType

class typeComponent(openType.openType):
    
    COMPONENT_NULL                      = 0x00
    COMPONENT_OPENWSN                   = 0x01
    #cross-layers
    COMPONENT_IDMANAGER                 = 0x02
    COMPONENT_OPENQUEUE                 = 0x03
    COMPONENT_OPENSERIAL                = 0x04
    COMPONENT_PACKETFUNCTIONS           = 0x05
    COMPONENT_RANDOM                    = 0x06
    #PHY
    COMPONENT_RADIO                     = 0x07
    #MAClow
    COMPONENT_IEEE802154                = 0x08
    COMPONENT_IEEE802154E               = 0x09
    
    
    
    
    
    #MAClow<->MAChigh ("virtual components")
    COMPONENT_RES_TO_IEEE802154E        = 0x0a
    COMPONENT_IEEE802154E_TO_RES        = 0x0b
    #MAChigh
    COMPONENT_RES                       = 0x0c
    COMPONENT_NEIGHBORS                 = 0x0d
    COMPONENT_SCHEDULE                  = 0x0e
    #IPHC
    COMPONENT_OPENBRIDGE                = 0x0f
    COMPONENT_IPHC                      = 0x10
    #IPv6
    COMPONENT_FORWARDING                = 0x11
    COMPONENT_ICMPv6                    = 0x12
    COMPONENT_ICMPv6ECHO                = 0x13
    COMPONENT_ICMPv6ROUTER              = 0x14
    COMPONENT_ICMPv6RPL                 = 0x15
    #TRAN
    COMPONENT_OPENTCP                   = 0x16
    COMPONENT_OPENUDP                   = 0x17
    COMPONENT_OPENCOAP                  = 0x18
    #App test
    COMPONENT_TCPECHO                   = 0x19
    COMPONENT_TCPINJECT                 = 0x1a
    COMPONENT_TCPPRINT                  = 0x1b
    COMPONENT_UDPECHO                   = 0x1c
    COMPONENT_UDPINJECT                 = 0x1d
    COMPONENT_UDPPRINT                  = 0x1e
    COMPONENT_RSVP                      = 0x1f
    #App
    COMPONENT_OHLONE                    = 0x20
    COMPONENT_HELI                      = 0x21
    COMPONENT_IMU                       = 0x22
    COMPONENT_RLEDS                     = 0x23
    COMPONENT_RREG                      = 0x24
    COMPONENT_RWELLKNOWN                = 0x25
    COMPONENT_RT                        = 0x26
    COMPONENT_REX                       = 0x27
    COMPONENT_RXL1                      = 0x28
    COMPONENT_RINFO                     = 0x29
    COMPONENT_RHELI                     = 0x2a
    COMPONENT_RRUBE                     = 0x2b
    COMPONENT_LAYERDEBUG                = 0x2c
    COMPONENT_UDPRAND                   = 0x2d
    COMPONENT_UDPSTORM                  = 0x2e
    COMPONENT_UDPLATENCY                = 0x2f
    COMPONENT_TEST                      = 0x30
    COMPONENT_R6T                       = 0x31
    COMPONENT_SWARMBAND                 = 0x32
    
    def __init__(self):
        # log
        log.info("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        return '{0} ({1})'.format(self.type,self.desc)
    
    #======================== public ==========================================
    
    def update(self,type):
        self.type = type
        
        if   type==self.COMPONENT_NULL:
            self.desc = 'NULL'
        elif type==self.COMPONENT_OPENWSN:
            self.desc = 'OPENWSN'
        
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
        elif type==self.COMPONENT_UDPSTORM:
            self.desc = 'UDPSTORM'
        elif type==self.COMPONENT_UDPLATENCY:
            self.desc = 'UDPLATENCY'
        elif type==self.COMPONENT_TEST:
            self.desc = 'TEST'
        elif type==self.COMPONENT_R6T:
            self.desc = 'R6T'
        elif type==self.COMPONENT_SWARMBAND:
            self.desc = 'SWARMBAND'
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    