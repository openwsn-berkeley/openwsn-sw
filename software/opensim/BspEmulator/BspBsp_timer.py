#!/usr/bin/python

import struct
import BspModule

class BspBsp_timer(BspModule.BspModule):
    '''
    \brief Emulates the 'bsp_timer' BSP module
    '''
    
    INTR_COMPARE  = 'bsp_timer.compare'
    
    def __init__(self,motehandler,timeline,hwCrystal):
        
        # store params
        self.motehandler     = motehandler
        self.timeline        = timeline
        self.hwCrystal       = hwCrystal
        
        # local variables
        self.counterVal      = 0
        self.compareArmed    = False    
        
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
        
        # unpack the parameters
        (self.delayTicks,)        = struct.unpack('<H', params)
        
        # log the activity
        self.log.debug('cmd_scheduleIn delayTicks='+str(self.delayTicks))
        
        # calculate time at overflow event (in 'period' ticks)
        compareTime               = self.hwCrystal.getTimeIn((self.delayTicks%0xffff))
        
        # schedule compare event
        self.timeline.scheduleEvent(compareTime,
                                    self.intr_compare,
                                    self.INTR_COMPARE)
        
        # the compare is now scheduled
        self.compareArmed         = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_bsp_timer_scheduleIn'])
    
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
    
    #===== interrupts
    
    def intr_compare(self):
        '''
        \brief A compare event happened.
        '''
        
        # send interrupt to mote
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_bsp_timer_isr'])
    
    #======================== private =========================================