# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('typeAsn')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import openType

class typeAsn(openType.openType):
    
    def __init__(self):
        # log
        log.info("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        return '0x{0}'.format(''.join(["%.2x"%b for b in self.asn]))
    
    #======================== public ==========================================
    
    def update(self,byte0_1,byte2_3,byte4):
        self.asn =  [
                        byte4,
                        byte2_3>>8,
                        byte2_3%256,
                        byte0_1>>8,
                        byte0_1%256,
                    ]
    
    #======================== private =========================================
    