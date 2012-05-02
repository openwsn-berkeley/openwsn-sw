#!/usr/bin/python

import BspModule

class BspUart(BspModule.BspModule):
    '''
    \brief Emulates the 'uart' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspUart')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_init'])
    
    def cmd_enableInterrupts(self,params):
        
        # log the activity
        self.log.debug('cmd_enableInterrupts')
        
        raise NotImplementedError()
    
    def cmd_disableInterrupts(self,params):
        
        # log the activity
        self.log.debug('cmd_disableInterrupts')
        
        raise NotImplementedError()
    
    def cmd_clearRxInterrupts(self,params):
        
        # log the activity
        self.log.debug('cmd_clearRxInterrupts')
        
        raise NotImplementedError()
    
    def cmd_clearTxInterrupts(self,params):
        
        # log the activity
        self.log.debug('cmd_clearTxInterrupts')
        
        raise NotImplementedError()
    
    def cmd_writeByte(self,params):
        
        # log the activity
        self.log.debug('cmd_writeByte')
        
        raise NotImplementedError()
    
    def cmd_readByte(self,params):
        
        # log the activity
        self.log.debug('cmd_readByte')
        
        raise NotImplementedError()
    
    #======================== private =========================================