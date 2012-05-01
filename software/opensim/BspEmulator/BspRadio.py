#!/usr/bin/python

import BspModule

class BspRadio(BspModule.BspModule):
    '''
    \brief Emulates the 'radio' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadio')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_reset(self):
        
        # log the activity
        self.log.debug('cmd_reset')
        
        raise NotImplementedError()
    
    def cmd_startTimer(self):
        
        # log the activity
        self.log.debug('cmd_startTimer')
        
        raise NotImplementedError()
    
    def cmd_getTimerValue(self):
        
        # log the activity
        self.log.debug('cmd_getTimerValue')
        
        raise NotImplementedError()
    
    def cmd_setTimerPeriod(self):
        
        # log the activity
        self.log.debug('cmd_setTimerPeriod')
        
        raise NotImplementedError()
    
    def cmd_getTimerPeriod(self):
        
        # log the activity
        self.log.debug('cmd_getTimerPeriod')
        
        raise NotImplementedError()
    
    def cmd_setFrequency(self):
        
        # log the activity
        self.log.debug('cmd_setFrequency')
        
        raise NotImplementedError()
    
    def cmd_rfOn(self):
        
        # log the activity
        self.log.debug('cmd_rfOn')
        
        raise NotImplementedError()
    
    def cmd_rfOff(self):
        
        # log the activity
        self.log.debug('cmd_rfOff')
        
        raise NotImplementedError()
    
    def cmd_loadPacket(self):
        
        # log the activity
        self.log.debug('cmd_loadPacket')
        
        raise NotImplementedError()
    
    def cmd_txEnable(self):
        
        # log the activity
        self.log.debug('cmd_txEnable')
        
        raise NotImplementedError()
    
    def cmd_txNow(self):
        
        # log the activity
        self.log.debug('cmd_txNow')
        
        raise NotImplementedError()
    
    def cmd_rxEnable(self):
        
        # log the activity
        self.log.debug('cmd_rxEnable')
        
        raise NotImplementedError()
    
    def cmd_rxNow(self):
        
        # log the activity
        self.log.debug('cmd_rxNow')
        
        raise NotImplementedError()
    
    def cmd_getReceivedFrame(self):
        
        # log the activity
        self.log.debug('cmd_getReceivedFrame')
        
        raise NotImplementedError()
    
    #======================== private =========================================