# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('typeRssi')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import openType

class typeRssi(openType.openType):
    
    def __init__(self):
        # log
        log.info("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        return '{0} dBm'.format(self.rssi)
    
    #======================== public ==========================================
    
    def update(self,rssi):
        self.rssi = rssi
    
    #======================== private =========================================
    