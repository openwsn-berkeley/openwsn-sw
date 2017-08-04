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

class BspSctimer(BspModule.BspModule):
    '''
    Emulates the 'sctimer' BSP module.
    '''
    
    INTR_COMPARE  = 'sctimer.compare'
    INTR_OVERFLOW = 'sctimer.overflow'
    ROLLOVER      = 0xffffffff + 1

    LOOP_THRESHOLD = 0xffffff+1
    
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
        self.intEnabled      = True
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspSctimer')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void sctimer_init()'''

        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')

        # reset the timer
        self._cmd_reset_internal()

        # remember the time of last reset
        self.timeLastReset = self.hwCrystal.getTimeLastTick()
        self.timeLastCompare = self.timeLastReset

        # calculate time at overflow event (in 'ROLLOVER' ticks)
        overflowTime = self.hwCrystal.getTimeIn(self.ROLLOVER)

        # schedule overflow event
        self.timeline.scheduleEvent(
            atTime=overflowTime,
            moteId=self.motehandler.getId(),
            cb=self.intr_overflow,
            desc=self.INTR_OVERFLOW,
        )

        # the counter is now running
        self.running       = True

        # disable interrupt for now
        self.intEnabled    = True

        # remember that module has been intialized
        self.isInitialized = False
    
    def cmd_setCompare(self,compareValue):
        '''
        emulates
        void sctimer_setCompare(PORT_TIMER_WIDTH compareValue)
        '''
        
        try:
            # enable interrupt
            self.cmd_enable()

            # log the activity
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('cmd_setCompare compareValue=' + str(compareValue))

            # get current counter value
            counterVal = self.hwCrystal.getTicksSince(self.timeLastReset)

            # how many ticks until compare event
            if counterVal - compareValue > 0 and counterVal - compareValue < self.LOOP_THRESHOLD:
                # we're already too late, schedule compare event right now
                ticksBeforeEvent = 0
            else:
                ticksBeforeEvent = compareValue - counterVal
                
            # print "compareValue {0} counterVal {1}  self.timeLastReset {2}".format(compareValue,counterVal, self.timeLastReset)

            # calculate time at overflow event
            compareTime = self.hwCrystal.getTimeIn(ticksBeforeEvent)

            # schedule compare event
            self.timeline.scheduleEvent(compareTime,
                                        self.motehandler.getId(),
                                        self.intr_compare,
                                        self.INTR_COMPARE)

            # the compare is now scheduled
            self.compareArmed = True
        
        except Exception as err:
            errMsg=u.formatCriticalMessage(err)
            print errMsg
            self.log.critical(errMsg)
    
    def cmd_readCounter(self):
        '''emulates
           uin16_t sctimer_readCounter()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_get_currentValue')
        
        # get current counter value
        counterVal           = self.hwCrystal.getTicksSince(self.timeLastReset)
        
        # respond
        return counterVal

    def cmd_enable(self):
        '''emulates
           void sctimer_enable()'''

        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_enable')

        self.intEnabled = True

    def cmd_disable(self):
        '''emulates
           void sctimer_disable()'''

        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_disable')

        # disbale interrupt
        self.intEnabled = False

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
        self.timeLastReset = self.hwCrystal.getTimeLastTick()

        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('timeLastReset=' + str(self.timeLastReset))
            self.log.debug('ROLLOVER=' + str(self.ROLLOVER))

        # reschedule the next overflow event
        # Note: the intr_overflow will fire every self.ROLLOVER
        nextOverflowTime = self.hwCrystal.getTimeIn(self.ROLLOVER)
        self.log.debug('nextOverflowTime=' + str(nextOverflowTime))
        self.timeline.scheduleEvent(
            atTime=nextOverflowTime,
            moteId=self.motehandler.getId(),
            cb=self.intr_overflow,
            desc=self.INTR_OVERFLOW,
        )
        
        print "cycle cycle\n"

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

        if self.intEnabled:
            # send interrupt to mote
            self.motehandler.mote.sctimer_isr()
        
        # kick the scheduler
        return True
    
    #======================== private =========================================