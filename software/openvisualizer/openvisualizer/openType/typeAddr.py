# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('typeAddr')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import openType

class typeAddr(openType.openType):
    
    ADDR_NONE    = 0
    ADDR_16B     = 1
    ADDR_64B     = 2
    ADDR_128B    = 3
    ADDR_PANID   = 4
    ADDR_PREFIX  = 5
    ADDR_ANYCAST = 6
    
    def __init__(self):
        # log
        log.info("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        output  = []
        if self.addr:
           output += ['-'.join(["%.2x"%b for b in self.addr])]
        output += [' ({0})'.format(self.desc)]
        return ''.join(output)
    
    #======================== public ==========================================
    
    def update(self,type,bodyH,bodyL):
        fullAddr = [
            bodyH>>(8*0) & 0xff,
            bodyH>>(8*1) & 0xff,
            bodyH>>(8*2) & 0xff,
            bodyH>>(8*3) & 0xff,
            bodyH>>(8*4) & 0xff,
            bodyH>>(8*5) & 0xff,
            bodyH>>(8*6) & 0xff,
            bodyH>>(8*7) & 0xff,
            bodyL>>(8*0) & 0xff,
            bodyL>>(8*1) & 0xff,
            bodyL>>(8*2) & 0xff,
            bodyL>>(8*3) & 0xff,
            bodyL>>(8*4) & 0xff,
            bodyL>>(8*5) & 0xff,
            bodyL>>(8*6) & 0xff,
            bodyL>>(8*7) & 0xff,
       ]
        self.type = type
        if   type==self.ADDR_NONE:
            self.desc = 'None'
            self.addr = None
        elif type==self.ADDR_16B:
            self.desc = '16b'
            self.addr = fullAddr[:2]
        elif type==self.ADDR_64B:
            self.desc = '64b'
            self.addr = fullAddr[:8]
        elif type==self.ADDR_128B:
            self.desc = '128b'
            self.addr = fullAddr
        elif type==self.ADDR_PANID:
            self.desc = 'panId'
            self.addr = fullAddr[:2]
        elif type==self.ADDR_PREFIX:
            self.desc = 'prefix'
            self.addr = fullAddr[:8]
        elif type==self.ADDR_ANYCAST:
            self.desc = 'anycast'
            self.addr = None
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    