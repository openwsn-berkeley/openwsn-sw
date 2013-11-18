#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
    
class Propagation(object):
    '''
    The propagation model of the engine.
    '''
    
    def __init__(self,engine):
        
        # store params
        self.engine               = engine
        
        # local variables
        
        # logging
        self.log                  = logging.getLogger('Propagation')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    