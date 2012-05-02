#!/usr/bin/python

import BspModule

class BspRadio(BspModule.BspModule):
    '''
    \brief Emulates the 'radio' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadio')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_reset(self,params):
        
        # log the activity
        self.log.debug('cmd_reset')
        
        raise NotImplementedError()
    
    def cmd_startTimer(self,params):
        
        # log the activity
        self.log.debug('cmd_startTimer')
        
        raise NotImplementedError()
    
    def cmd_getTimerValue(self,params):
        
        # log the activity
        self.log.debug('cmd_getTimerValue')
        
        raise NotImplementedError()
    
    def cmd_setTimerPeriod(self,params):
        
        # log the activity
        self.log.debug('cmd_setTimerPeriod')
        
        raise NotImplementedError()
    
    def cmd_getTimerPeriod(self,params):
        
        # log the activity
        self.log.debug('cmd_getTimerPeriod')
        
        raise NotImplementedError()
    
    def cmd_setFrequency(self,params):
        
        # log the activity
        self.log.debug('cmd_setFrequency')
        
        raise NotImplementedError()
    
    def cmd_rfOn(self,params):
        
        # log the activity
        self.log.debug('cmd_rfOn')
        
        raise NotImplementedError()
    
    def cmd_rfOff(self,params):
        
        # log the activity
        self.log.debug('cmd_rfOff')
        
        raise NotImplementedError()
    
    def cmd_loadPacket(self,params):
        
        # log the activity
        self.log.debug('cmd_loadPacket')
        
        raise NotImplementedError()
    
    def cmd_txEnable(self,params):
        
        # log the activity
        self.log.debug('cmd_txEnable')
        
        raise NotImplementedError()
    
    def cmd_txNow(self,params):
        
        # log the activity
        self.log.debug('cmd_txNow')
        
        raise NotImplementedError()
    
    def cmd_rxEnable(self,params):
        
        # log the activity
        self.log.debug('cmd_rxEnable')
        
        raise NotImplementedError()
    
    def cmd_rxNow(self,params):
        
        # log the activity
        self.log.debug('cmd_rxNow')
        
        raise NotImplementedError()
    
    def cmd_getReceivedFrame(self,params):
        
        # log the activity
        self.log.debug('cmd_getReceivedFrame')
        
        raise NotImplementedError()
    
    #======================== private =========================================