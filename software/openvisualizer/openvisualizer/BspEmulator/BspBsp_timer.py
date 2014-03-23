#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine     import SimEngine
import openvisualizer.openvisualizer_utils as u
import BspModule

class BspBsp_timer(BspModule.BspModule):
    '''
    Emulates the 'bsp_timer' BSP module.
    '''
    
    INTR_COMPARE  = 'bsp_timer.compare'
    INTR_OVERFLOW = 'bsp_timer.overflow'
    ROLLOVER      = 0xffff+1
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        self.timeline        = self.engine.timeline
        self.hwCrystal       = self.motehandler.hwCrystal
        self.running         = False
        self.compareArmed    = False
        self.timeLastReset   = None
        self.timeLastCompare = None
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBsp_timer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void bsp_timer_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # reset the timer
        self._cmd_reset_internal()
        
        # remember the time of last reset
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        self.timeLastCompare = self.timeLastReset
        
        # calculate time at overflow event (in 'ROLLOVER' ticks)
        overflowTime         = self.hwCrystal.getTimeIn(self.ROLLOVER)
        
        # schedule overflow event
        self.timeline.scheduleEvent(
            atTime = overflowTime,
            moteId = self.motehandler.getId(),
            cb     = self.intr_overflow,
            desc   = self.INTR_OVERFLOW,
        )
        
        # the counter is now running
        self.running         = True
        
        # remember that module has been intialized
        self.isInitialized   = True
    
    def cmd_reset(self):
        '''emulates
           void bsp_timer_reset()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_reset')
        
        self._cmd_reset_internal()
    
    def cmd_scheduleIn(self,delayTicks):
        '''
        emulates
        void bsp_timer_scheduleIn(PORT_TIMER_WIDTH delayTicks)
        '''
        
        try:
        
            # log the activity
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('cmd_scheduleIn delayTicks='+str(delayTicks))
            
            # get number of ticks since last compare
            ticksSinceCompare         = self.hwCrystal.getTicksSince(self.timeLastCompare)
            
            # how many ticks until compare event
            if ticksSinceCompare>delayTicks:
                # we're already too late, schedule compare event right now
                
                ticksBeforeEvent      = 0
            else:
                ticksBeforeEvent      = delayTicks-ticksSinceCompare
            
            # calculate time at overflow event (in 'period' ticks)
            compareTime               = self.hwCrystal.getTimeIn(ticksBeforeEvent)
            
            # schedule compare event
            self.timeline.scheduleEvent(
                atTime = compareTime,
                moteId = self.motehandler.getId(),
                cb     = self.intr_compare,
                desc   = self.INTR_COMPARE,
            )
            
            # the compare is now scheduled
            self.compareArmed         = True
        
        except Exception as err:
            errMsg=u.formatCriticalMessage(err)
            print errMsg
            log.critical(errMsg)
    
    def cmd_cancel_schedule(self):
        '''emulates
           void bsp_timer_cancel_schedule()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_cancel_schedule')
        
        # cancel the compare event
        numCanceled = self.timeline.cancelEvent(
            moteId = self.motehandler.getId(),
            desc   = self.INTR_COMPARE,
        )
        assert(numCanceled<=1)
    
    def cmd_get_currentValue(self):
        '''emulates
           uin16_t bsp_timer_get_currentValue()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_get_currentValue')
        
        # get current counter value
        counterVal           = self.hwCrystal.getTicksSince(self.timeLastReset)
        
        # respond
        return counterVal
    
    #======================== private =========================================
    
    def _cmd_reset_internal(self):
        
        # cancel the compare event
        self.compareArmed    = False
        numCanceled = self.timeline.cancelEvent(
            moteId = self.motehandler.getId(),
            desc   = self.INTR_COMPARE,
        )
        assert(numCanceled<=1)
        
        # cancel the (internal) overflow event
        self.running    = False
        numCanceled     = self.timeline.cancelEvent(
            moteId = self.motehandler.getId(),
            desc   = self.INTR_OVERFLOW,
        )
        assert(numCanceled<=1)
        
        # reset the counter value
        self.counterVal      = 0
        
        # remember the time of last reset
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        self.timeLastCompare = self.timeLastReset
        
        # calculate time at overflow event (in 'ROLLOVER' ticks)
        overflowTime         = self.hwCrystal.getTimeIn(self.ROLLOVER)
        
        # schedule overflow event
        
        self.timeline.scheduleEvent(
            atTime = overflowTime,
            moteId = self.motehandler.getId(),
            cb     = self.intr_overflow,
            desc   = self.INTR_OVERFLOW,
        )
    
    #======================== interrupts ======================================
    
    def intr_overflow(self):
        '''
        An (internal) overflow event happened.
        '''
        
        # remember the time of this reset; needed internally to schedule further events
        self.timeLastReset   = self.hwCrystal.getTimeLastTick()
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('timeLastReset='+str(self.timeLastReset))
            self.log.debug('ROLLOVER='+str(self.ROLLOVER))
        
        # reschedule the next overflow event
        # Note: the intr_overflow will fire every self.ROLLOVER
        nextOverflowTime     = self.hwCrystal.getTimeIn(self.ROLLOVER)
        self.log.debug('nextOverflowTime='+str(nextOverflowTime))
        self.timeline.scheduleEvent(
            atTime = nextOverflowTime,
            moteId = self.motehandler.getId(),
            cb     = self.intr_overflow,
            desc   = self.INTR_OVERFLOW,
        )
        
        # do NOT kick the scheduler
        return False
        
    def intr_compare(self):
        '''
        A compare event happened.
        '''
        # remember the time of this comparison.
        self.timeLastCompare    = self.hwCrystal.getTimeLastTick()
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('timeLastCompare='+str(self.timeLastCompare))
            self.log.debug('ROLLOVER='+str(self.ROLLOVER))
        
        # send interrupt to mote
        self.motehandler.mote.bsp_timer_isr()
        
        # kick the scheduler
        return True
    
    #======================== private =========================================