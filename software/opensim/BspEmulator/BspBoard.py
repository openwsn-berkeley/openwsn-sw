#!/usr/bin/python

import logging

import BspModule

class BspBoard(BspModule.BspModule):
    '''
    \brief Emulates the 'board' BSP module
    '''
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine          = engine
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