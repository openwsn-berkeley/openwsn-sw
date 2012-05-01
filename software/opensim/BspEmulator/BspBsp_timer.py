#!/usr/bin/python

import BspModule

class BspBsp_timer(BspModule.BspModule):
    '''
    \brief Emulates the 'bsp_timer' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBsp_timer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_reset(self):
        
        # log the activity
        self.log.debug('cmd_reset')
        
        raise NotImplementedError()
    
    def cmd_scheduleIn(self):
    
        # log the activity
        self.log.debug('cmd_scheduleIn')
        
        raise NotImplementedError()
    
    def cmd_cancel_schedule(self):
        
        # log the activity
        self.log.debug('cmd_cancel_schedule')
        
        raise NotImplementedError()
    
    #======================== private =========================================
    
    def getIsInitialized():
       return self.isInitialized