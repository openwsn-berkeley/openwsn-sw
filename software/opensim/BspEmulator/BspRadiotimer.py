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
        '''emulates
           void radiotimer_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_init'])
    
    def cmd_start(self,params):
        '''emulates
           void radiotimer_start(uint16_t period)'''
        
        # log the activity
        self.log.debug('cmd_start')
        
        raise NotImplementedError()
    
    def cmd_getValue(self,params):
        '''emulates
           uint16_t radiotimer_getValue()'''
        
        # log the activity
        self.log.debug('cmd_getValue')
        
        raise NotImplementedError()
    
    def cmd_setPeriod(self,params):
        '''emulates
           void radiotimer_setPeriod(uint16_t period)'''
        
        # log the activity
        self.log.debug('cmd_setPeriod')
        
        raise NotImplementedError()
    
    def cmd_getPeriod(self,params):
        '''emulates
           uint16_t radiotimer_getPeriod()'''
        
        # log the activity
        self.log.debug('cmd_getPeriod')
        
        raise NotImplementedError()
    
    def cmd_schedule(self,params):
        '''emulates
           void radiotimer_schedule(uint16_t offset)'''
        
        # log the activity
        self.log.debug('cmd_schedule')
        
        raise NotImplementedError()
    
    def cmd_cancel(self,params):
        '''emulates
           void radiotimer_cancel()'''
        
        # log the activity
        self.log.debug('cmd_cancel')
        
        raise NotImplementedError()
    
    def cmd_getCapturedTime(self,params):
        '''emulates
           uint16_t radiotimer_getCapturedTime()'''
        
        # log the activity
        self.log.debug('cmd_getCapturedTime')
        
        raise NotImplementedError()
    
    #======================== private =========================================