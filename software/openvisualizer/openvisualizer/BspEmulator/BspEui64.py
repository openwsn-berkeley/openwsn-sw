#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine   import SimEngine
import BspModule

class BspEui64(BspModule.BspModule):
    '''
    Emulates the 'eui64' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspEui64')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_get(self):
        '''emulates
           void eui64_get(uint8_t* addressToWrite)'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_get')
        
        # get my 16-bit ID
        myId    = self.motehandler.getId()
        
        # format my EUI64
        myEui64 = [0x14,0x15,0x92,0xcc,0x00,0x00,((myId>>8) & 0xff),
                                                 ((myId>>0) & 0xff)]
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('returning '+str(myEui64))
        
        # respond
        return myEui64
    
    #======================== private =========================================