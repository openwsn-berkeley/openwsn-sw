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
    COMPONENT_SIXTOP_TO_IEEE802154E     = 0x0a
    COMPONENT_IEEE802154E_TO_SIXTOP     = 0x0b
    #MAChigh
    COMPONENT_SIXTOP                    = 0x0c
    COMPONENT_NEIGHBORS                 = 0x0d
    COMPONENT_SCHEDULE                  = 0x0e
    COMPONENT_SIXTOP_RES                = 0x0f
    #IPHC
    COMPONENT_OPENBRIDGE                = 0x10
    COMPONENT_IPHC                      = 0x11
    #IPv6
    COMPONENT_FORWARDING                = 0x12
    COMPONENT_ICMPv6                    = 0x13
    COMPONENT_ICMPv6ECHO                = 0x14
    COMPONENT_ICMPv6ROUTER              = 0x15
    COMPONENT_ICMPv6RPL                 = 0x16
    #TRAN
    COMPONENT_OPENTCP                   = 0x17
    COMPONENT_OPENUDP                   = 0x18
    COMPONENT_OPENCOAP                  = 0x19
    #applications
    COMPONENT_C6T                       = 0x1a
    COMPONENT_CEXAMPLE                  = 0x1b
    COMPONENT_CINFO                     = 0x1c
    COMPONENT_CLEDS                     = 0x1d
    COMPONENT_CSENSORS                  = 0x1e
    COMPONENT_CSTORM                    = 0x1f
    COMPONENT_CWELLKNOWN                = 0x20
    COMPONENT_TECHO                     = 0x21
    COMPONENT_TOHLONE                   = 0x22
    COMPONENT_UECHO                     = 0x23
    COMPONENT_UINJECT                   = 0x24
    COMPONENT_RRT                       = 0x25
    COMPONENT_SECURITY                  = 0x26
    COMPONENT_USERIALBRIDGE             = 0x27
    COMPONENT_UEXPIRATION               = 0x28
    COMPONENT_UMONITOR                  = 0x29
    
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
        
        elif type==self.COMPONENT_SIXTOP_TO_IEEE802154E:
            self.desc = 'SIXTOP_TO_IEEE802154E'
        elif type==self.COMPONENT_IEEE802154E_TO_SIXTOP:
            self.desc = 'IEEE802154E_TO_SIXTOP'
        
        elif type==self.COMPONENT_SIXTOP:
            self.desc = 'SIXTOP'
        elif type==self.COMPONENT_SIXTOP_RES:
            self.desc = 'SIXTOP_RES'
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
        
        elif type==self.COMPONENT_C6T:
            self.desc = 'C6T'
        elif type==self.COMPONENT_CEXAMPLE:
            self.desc = 'CEXAMPLE'
        elif type==self.COMPONENT_CINFO:
            self.desc = 'CINFO'
        elif type==self.COMPONENT_CLEDS:
            self.desc = 'CLEDS'
        elif type==self.COMPONENT_CSENSORS:
            self.desc = 'CSENSORS'
        elif type==self.COMPONENT_CWELLKNOWN:
            self.desc = 'CWELLKNOWN'
        elif type==self.COMPONENT_CSTORM:
            self.desc = 'COMPONENT_CSTORM'
        
        elif type==self.COMPONENT_TECHO:
            self.desc = 'TECHO'
        elif type==self.COMPONENT_TOHLONE:
            self.desc = 'TOHLONE'
        
        elif type==self.COMPONENT_UECHO:
            self.desc = 'UECHO'
        elif type==self.COMPONENT_UINJECT:
            self.desc = 'COMPONENT_UINJECT'
        
        elif type==self.COMPONENT_RRT:
            self.desc = 'RRT'
            
        elif type==self.COMPONENT_SECURITY:
            self.desc = 'SECURITY'
            
        elif type==self.COMPONENT_UEXPIRATION:
            self.desc = 'UEXPIRATION'
            
        elif type==self.COMPONENT_UMONITOR:
            self.desc = 'UMONITOR'
            
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    
