#!/usr/bin/python

import random
import math
import HwModule

class HwCrystal(HwModule.HwModule):
    '''
    \brief Emulates the mote's crystal.
    '''
    
    def __init__(self,motehandler,timeline,frequency,maxDrift=0):
        
        # store params
        self.motehandler     = motehandler
        self.timeline        = timeline
        self.frequency       = frequency
        self.maxDrift        = maxDrift
        
        # local variables
        self.drift           = float(random.uniform(-self.maxDrift,
                                                    +self.maxDrift))
        
        # initialize the parent
        HwModule.HwModule.__init__(self,'HwCrystal')
    
    #======================== public ==========================================
    
    def start(self):
        '''
        \brief Start the crystal.
        '''
        
        self.tsTick          = self.timeline.getCurrentTime()
    
    def getTimeLastTick(self):
        '''
        \brief Return the timestamp of the last tick.
        
        \returns The timestamp of the last tick.
        '''
        
        currentTime          = self.timeline.getCurrentTime()
        timeSinceLast        = currentTime-self.tsTick
        period               = self._getPeriod()
        
        numTicksSinceLast    = math.floor(float(timeSinceLast)/float(period))
        timeLastTick         = self.tsTick+numTicksSinceLast*period
        
        self.tsTick          = timeLastTick
        
        return timeLastTick
    
    def getTimeIn(self,numticks):
        '''
        \brief Return the time it will be in a given number of ticks.
        
        \params numticks The number of ticks of interest.
        
        \returns The time it will be in a given number of ticks.
        '''
        
        timeLastTick         = self.getTimeLastTick()
        period               = self._getPeriod()
        
        return timeLastTick+numticks*period
    
    #======================== private =========================================
    
    def _getPeriod(self):
        
        period               = float(1)/float(self.frequency)             # nominal period
        period              += float(self.drift)*float(period/1000000)    # apply drift
        
        return period
        