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

class typeCellType(openType.openType):
    
    CELLTYPE_OFF             = 0
    CELLTYPE_TX              = 1
    CELLTYPE_RX              = 2
    CELLTYPE_TXRX            = 3
    CELLTYPE_SERIALRX        = 4
    CELLTYPE_MORESERIALRX    = 5
    
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
        if   type==self.CELLTYPE_OFF:
            self.desc = 'OFF'
        elif type==self.CELLTYPE_TX:
            self.desc = 'TX'
        elif type==self.CELLTYPE_RX:
            self.desc = 'RX'
        elif type==self.CELLTYPE_TXRX:
            self.desc = 'TXRX'
        elif type==self.CELLTYPE_SERIALRX:
            self.desc = 'SERIALRX'
        elif type==self.CELLTYPE_MORESERIALRX:
            self.desc = 'MORESERIALRX'
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    