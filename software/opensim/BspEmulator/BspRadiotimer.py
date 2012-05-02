#!/usr/bin/python

import BspModule

class BspRadiotimer(BspModule.BspModule):
    '''
    \brief Emulates the 'radiotimer' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadiotimer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_init'])
    
    def cmd_start(self,params):
        
        # log the activity
        self.log.debug('cmd_start')
        
        raise NotImplementedError()
    
    def cmd_getValue(self,params):
        
        # log the activity
        self.log.debug('cmd_getValue')
        
        raise NotImplementedError()
    
    def cmd_setPeriod(self,params):
        
        # log the activity
        self.log.debug('cmd_setPeriod')
        
        raise NotImplementedError()
    
    def cmd_getPeriod(self,params):
        
        # log the activity
        self.log.debug('cmd_getPeriod')
        
        raise NotImplementedError()
    
    def cmd_schedule(self,params):
        
        # log the activity
        self.log.debug('cmd_schedule')
        
        raise NotImplementedError()
    
    def cmd_cancel(self,params):
        
        # log the activity
        self.log.debug('cmd_cancel')
        
        raise NotImplementedError()
    
    def cmd_getCapturedTime(self,params):
        
        # log the activity
        self.log.debug('cmd_getCapturedTime')
        
        raise NotImplementedError()
    
    #======================== private =========================================