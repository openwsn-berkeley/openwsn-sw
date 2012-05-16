#!/usr/bin/python

import BspModule

class BspBsp_timer(BspModule.BspModule):
    '''
    \brief Emulates the 'bsp_timer' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        self.counterVal = 0
        self.timerOn    = False
        self.timerOn    = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBsp_timer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        '''emulates
           void bsp_timer_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_bsp_timer_init'])
    
    def cmd_reset(self,params):
        '''emulates
           void bsp_timer_reset()'''
        
        # log the activity
        self.log.debug('cmd_reset')
        
        raise NotImplementedError()
    
    def cmd_scheduleIn(self,params):
        '''emulates
           void bsp_timer_scheduleIn(PORT_TIMER_WIDTH delayTicks)'''
    
        # log the activity
        self.log.debug('cmd_scheduleIn')
        
        raise NotImplementedError()
    
    def cmd_cancel_schedule(self,params):
        '''emulates
           void bsp_timer_cancel_schedule()'''
        
        # log the activity
        self.log.debug('cmd_cancel_schedule')
        
        raise NotImplementedError()
    
    def cmd_get_currentValue(self,params):
        '''emulates
           uin16_t bsp_timer_get_currentValue()'''
        
        # log the activity
        self.log.debug('cmd_get_currentValue')
        
        raise NotImplementedError()
    
    #======================== private =========================================