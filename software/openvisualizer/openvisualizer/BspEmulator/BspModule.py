#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

class BspModule(object):
    '''
    Emulates the 'board' BSP module
    '''
    
    def __init__(self,name):
        
        # store params
        
        # local variables
        self.isInitialized = False
        
        # logging
        self.log  = logging.getLogger(name+'_'+str(self.motehandler.getId()))
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
    
    #======================== public ==========================================
    
    #=== getters
    
    def getIsInitialized():
       return self.isInitialized
    
    #======================== private =========================================
    
    def _checkInit(self):
        assert self.isInitialized
    