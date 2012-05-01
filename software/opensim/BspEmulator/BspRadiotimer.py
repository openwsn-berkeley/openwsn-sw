#!/usr/bin/python

import BspModule

class BspRadiotimer(BspModule.BspModule):
    '''
    \brief Emulates the 'radiotimer' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadiotimer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_start(self):
        
        # log the activity
        self.log.debug('cmd_start')
        
        raise NotImplementedError()
    
    def cmd_getValue(self):
        
        # log the activity
        self.log.debug('cmd_getValue')
        
        raise NotImplementedError()
    
    def cmd_setPeriod(self):
        
        # log the activity
        self.log.debug('cmd_setPeriod')
        
        raise NotImplementedError()
    
    def cmd_getPeriod(self):
        
        # log the activity
        self.log.debug('cmd_getPeriod')
        
        raise NotImplementedError()
    
    def cmd_schedule(self):
        
        # log the activity
        self.log.debug('cmd_schedule')
        
        raise NotImplementedError()
    
    def cmd_cancel(self):
        
        # log the activity
        self.log.debug('cmd_cancel')
        
        raise NotImplementedError()
    
    def cmd_getCapturedTime(self):
        
        # log the activity
        self.log.debug('cmd_getCapturedTime')
        
        raise NotImplementedError()
    
    #======================== private =========================================