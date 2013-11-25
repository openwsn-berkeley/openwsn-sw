#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging

import SimEngine

class IdManager(object):
    '''
    The module which assigns ID to the motes.
    '''
    
    def __init__(self):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        
        # local variables
        self.currentId            = 0
        
        # logging
        self.log                  = logging.getLogger('IdManager')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
        
    
    #======================== public ==========================================
    
    def getId(self):
        
        # increment the running ID
        self.currentId += 1
        
        # debug
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('assigning ID='+str(self.currentId))
        
        return self.currentId
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    