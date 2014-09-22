# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('openType')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

class openType(object):
    
    def __init__(self):
        # log
        log.info("creating object")
        
        self.initialized = None
    
    #======================== public ==========================================
    
    def initFromBytes(self,byteArray):
        raise NotImplementedError
    
    def initFromFields(self,fields):
        raise NotImplementedError
    
    #======================== private =========================================
    