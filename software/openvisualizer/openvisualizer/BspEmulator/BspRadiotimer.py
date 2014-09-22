#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine     import SimEngine
import BspModule

class BspRadiotimer(BspModule.BspModule):
    '''
    Emulates the 'radiotimer' BSP module
    '''
    
    INTR_COMPARE  = 'radiotimer.compare'
    INTR_OVERFLOW = 'radiotimer.overflow'
    OVERFLOW      = 0xffff+1
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        self.timeline        = self.engine.timeline
        self.hwCrystal       = self.motehandler.hwCrystal
        self.running         = False   # whether the counter is currently running
        self.timeLastReset   = None    # time at last counter reset
        self.period          = None    # counter period
        self.compareArmed    = False   # whether the compare is armed
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadiotimer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void radiotimer_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
    
    def cmd_start(self,period):
        '''emulates
           void radiotimer_start(uint16_t period)'''
        
        # store params
        self.period          = period
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_start period='+str(self.period))
        
        # remember the time of last reset
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        
        # calculate time at overflow event (in 'period' ticks)
        overflowTime         = self.hwCrystal.getTimeIn(self.period)
        
        # schedule overflow event
        self.timeline.scheduleEvent(overflowTime,
                                    self.motehandler.getId(),
                                    self.intr_overflow,
                                    self.INTR_OVERFLOW)

        # the counter is now running
        self.running         = True
    
    def cmd_getValue(self):
        '''emulates
           uint16_t radiotimer_getValue()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_getValue')
        
        # get current counter value
        counterVal           = self.hwCrystal.getTicksSince(self.timeLastReset)
        
        # respond
        return counterVal
    
    def cmd_setPeriod(self,period):
        '''emulates
           void radiotimer_setPeriod(uint16_t period)'''
        
        # store params
        self.period          = period
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_setPeriod period='+str(self.period))
        
        # how many ticks since last reset
        ticksSinceReset      = self.hwCrystal.getTicksSince(self.timeLastReset)
        
        # calculate time at overflow event (in 'period' ticks)
        if ticksSinceReset<self.period:
            ticksBeforeEvent = self.period-ticksSinceReset
        else:
            ticksBeforeEvent = self.OVERFLOW-ticksSinceReset+self.period
        
        # calculate time at overflow event (in 'period' ticks)
        overflowTime         = self.hwCrystal.getTimeIn(ticksBeforeEvent)
        
        # schedule overflow event
        self.timeline.scheduleEvent(overflowTime,
                                    self.motehandler.getId(),
                                    self.intr_overflow,
                                    self.INTR_OVERFLOW)
    
    def cmd_getPeriod(self):
        '''emulates
           uint16_t radiotimer_getPeriod()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_getPeriod')
        
        # respond
        return self.period
    
    def cmd_schedule(self,offset):
        '''emulates
           void radiotimer_schedule(uint16_t offset)'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
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
                                    self.motehandler.getId(),
                                    self.intr_compare,
                                    self.INTR_COMPARE)
                                    
        # the compare is now scheduled
        self.compareArmed    = True
    
    def cmd_cancel(self):
        '''emulates
           void radiotimer_cancel()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_cancel')
        
        # cancel the compare event
        numCanceled = self.timeline.cancelEvent(self.motehandler.getId(),
                                                self.INTR_COMPARE)
        assert(numCanceled<=1)
    
    def cmd_getCapturedTime(self):
        '''emulates
           uint16_t radiotimer_getCapturedTime()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_getCapturedTime')
        
        raise NotImplementedError()
    
    def getCounterVal(self):
        return self.hwCrystal.getTicksSince(self.timeLastReset)
    
    #======================== interrupts ======================================
    
    def intr_compare(self):
        '''
        A compare event happened.
        '''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('intr_compare')
        
        # reschedule the next compare event
        # Note: as long as radiotimer_cancel() is not called, the intr_compare
        #       will fire every self.period
        nextCompareTime      = self.hwCrystal.getTimeIn(self.period)
        self.timeline.scheduleEvent(nextCompareTime,
                                    self.motehandler.getId(),
                                    self.intr_compare,
                                    self.INTR_COMPARE)
        
        # send interrupt to mote
        self.motehandler.mote.radiotimer_isr_compare()
        
        # kick the scheduler
        return True
    
    def intr_overflow(self):
        '''
        An overflow event happened.
        '''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('intr_overflow')
        
        # remember the time of this reset; needed internally to schedule further events
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        
        # reschedule the next overflow event
        # Note: the intr_overflow fires every self.period
        nextOverflowTime     = self.hwCrystal.getTimeIn(self.period)
        self.timeline.scheduleEvent(
            nextOverflowTime,
            self.motehandler.getId(),
            self.intr_overflow,
            self.INTR_OVERFLOW
        )
        
        # send interrupt to mote
        self.motehandler.mote.radiotimer_isr_overflow()
        
        # kick the scheduler
        return True
    
    #======================== private =========================================
    
    