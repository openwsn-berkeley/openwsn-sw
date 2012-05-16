#!/usr/bin/python

import struct
import BspModule

class BspRadiotimer(BspModule.BspModule):
    '''
    \brief Emulates the 'radiotimer' BSP module
    '''
    
    INTR_COMPARE  = 'radiotimer.compare'
    INTR_OVERFLOW = 'radiotimer.overflow'
    
    def __init__(self,motehandler,timeline,hwCrystal):
        
        # store params
        self.motehandler     = motehandler
        self.timeline        = timeline
        self.hwCrystal       = hwCrystal
        
        # local variables
        self.running         = False   # whether the counter is currently running
        self.timeLastReset   = None    # time at last counter reset
        self.period          = None    # counter period
        self.compareArmed    = False   # whether the compare is armed
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadiotimer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        '''emulates
           void radiotimer_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_init'])
    
    def cmd_start(self,params):
        '''emulates
           void radiotimer_start(uint16_t period)'''
        
        # unpack the parameters
        (self.period,)            = struct.unpack('<H', params)
        
        # log the activity
        self.log.debug('cmd_start period='+str(self.period))
        
        # remember the time of last reset
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        
        # calculate time at overflow event (in 'period' ticks)
        overflowTime         = self.hwCrystal.getTimeIn(self.period)
        
        # schedule overflow event
        self.timeline.scheduleEvent(overflowTime,
                                    self.intr_overflow,
                                    self.INTR_OVERFLOW)

        # the counter is now running
        self.running         = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_start'])
    
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
        
        # unpack the parameters
        (offset,)            = struct.unpack('<H', params)
        
        # log the activity
        self.log.debug('cmd_schedule offset='+str(offset))
        
        # get current counter value
        counterVal           = self.hwCrystal.getTicksSince(self.timeLastReset)
        
        # how many ticks until compare event
        if counterVal<offset:
            ticksBeforeEvent = offset-counterVal
        else:
            ticksBeforeEvent = self.period-counterVal+offset
        
        # calculate time at overflow event
        compareTime          = self.hwCrystal.getTimeIn(ticksBeforeEvent)
        
        # schedule compare event
        self.timeline.scheduleEvent(compareTime,
                                    self.intr_compare,
                                    self.INTR_COMPARE)
                                    
        # the compare is now scheduled
        self.compareArmed    = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_schedule'])
    
    def cmd_cancel(self,params):
        '''emulates
           void radiotimer_cancel()'''
        
        # log the activity
        self.log.debug('cmd_cancel')
        
        # cancel the compare event
        numCanceled = self.timeline.cancelEvent(self.INTR_COMPARE)
        
        # make sure that I did not cancel more than 1
        assert(numCanceled<=1)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_cancel'])
    
    def cmd_getCapturedTime(self,params):
        '''emulates
           uint16_t radiotimer_getCapturedTime()'''
        
        # log the activity
        self.log.debug('cmd_getCapturedTime')
        
        raise NotImplementedError()
    
    #===== interrupts
    
    def intr_compare(self):
        '''
        \brief A compare event happened.
        '''
        
        # reschedule the next compare event
        # Note: as long as radiotimer_cancel() is not called, the intr_compare
        #       will fire every self.period
        nextCompareTime      = self.hwCrystal.getTimeIn(self.period)
        self.timeline.scheduleEvent(nextCompareTime,
                                    self.intr_compare,
                                    self.INTR_COMPARE)
        
        # send interrupt to mote
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_isr_compare'])
    
    def intr_overflow(self):
        # remember the time of this reset; needed internally to schedule further events
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        
        # reschedule the next overflow event
        # Note: the intr_overflow will fire every self.period
        nextOverflowTime     = self.hwCrystal.getTimeIn(self.period)
        self.timeline.scheduleEvent(nextOverflowTime,
                                    self.intr_overflow,
                                    self.INTR_OVERFLOW)
    
        # send interrupt to mote
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radiotimer_isr_overflow'])
    
    #======================== private =========================================
    
    