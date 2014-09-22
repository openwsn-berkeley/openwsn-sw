#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine     import SimEngine
import BspModule

class BspBoard(BspModule.BspModule):
    '''
    Emulates the 'board' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        self.timeline        = self.engine.timeline
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBoard')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates:
           void board_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # remember that module has been initialized
        self.isInitialized = True
    
    def cmd_sleep(self):
        '''emulates
           void board_init()'''
        
        try:
            # log the activity
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('cmd_sleep')
            
            self.motehandler.cpuDone.release()
            
            # block the mote until CPU is released by ISR
            self.motehandler.cpuRunning.acquire()
            
        except Exception as err:
            self.log.critical(err)
    
    #======================== private =========================================