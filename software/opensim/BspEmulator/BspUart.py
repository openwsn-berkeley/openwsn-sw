#!/usr/bin/python

import BspModule

class BspUart(BspModule.BspModule):
    '''
    \brief Emulates the 'uart' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspUart')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_enableInterrupts(self):
        
        # log the activity
        self.log.debug('cmd_enableInterrupts')
        
        raise NotImplementedError()
    
    def cmd_disableInterrupts(self):
        
        # log the activity
        self.log.debug('cmd_disableInterrupts')
        
        raise NotImplementedError()
    
    def cmd_clearRxInterrupts(self):
        
        # log the activity
        self.log.debug('cmd_clearRxInterrupts')
        
        raise NotImplementedError()
    
    def cmd_clearTxInterrupts(self):
        
        # log the activity
        self.log.debug('cmd_clearTxInterrupts')
        
        raise NotImplementedError()
    
    def cmd_writeByte(self):
        
        # log the activity
        self.log.debug('cmd_writeByte')
        
        raise NotImplementedError()
    
    def cmd_readByte(self):
        
        # log the activity
        self.log.debug('cmd_readByte')
        
        raise NotImplementedError()
    
    #======================== private =========================================