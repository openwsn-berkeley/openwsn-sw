#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging
import random
import math

from openvisualizer.SimEngine     import SimEngine
import HwModule

class HwCrystal(HwModule.HwModule):
    '''
    Emulates the mote's crystal.
    '''
    
    FREQUENCY = 32768
    MAXDRIFT  = 0
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        self.timeline        = self.engine.timeline
        self.frequency       = self.FREQUENCY
        self.maxDrift        = self.MAXDRIFT
        
        # local variables
        self.drift           =  float(
                                    random.uniform(
                                        -self.maxDrift,
                                        +self.maxDrift
                                    )
                                )
        
        # the duration of one tick. Since it is constant, it is only calculated
        # once by _getPeriod(). Therefore, do not use directly, rather use
        # _getPeriod()
        self._period         = None
        
        # tsTick is a timestamp associated with any tick in the past. Since the
        # period is constant, it is used to ensure alignement of timestamps
        # to an integer number of ticks.
        self.tsTick          = None
        
        # initialize the parent
        HwModule.HwModule.__init__(self,'HwCrystal')
    
    #======================== public ==========================================
    
    def start(self):
        '''
        Start the crystal.
        '''
        
        # get the timestamp of a 
        self.tsTick          = self.timeline.getCurrentTime()
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('crystal starts at '+str(self.tsTick))
    
    def getTimeLastTick(self):
        '''
        Return the timestamp of the last tick.
        
     self.tsTick                currentTime                                    
          |                          |                   period                
          V                          v                <---------->             
        -----------------------------------------------------------------------
          |          |   ...    |          |          |          |          |  
        -----------------------------------------------------------------------
           <------------------------->                                          
                 timeSinceLast                                                 
                                ^                                              
                                |                                              
                           timeLastTick                                        
        
        :returns: The timestamp of the last tick.
        '''
        
        # make sure crystal has been started
        assert self.tsTick is not None

        currentTime          = self.timeline.getCurrentTime()
        timeSinceLast        = currentTime-self.tsTick
        period               = self._getPeriod()
        
        ticksSinceLast       = round(float(timeSinceLast)/float(period))
        timeLastTick         = self.tsTick+ticksSinceLast*period
        
        self.tsTick          = timeLastTick
        
        return timeLastTick
    
    def getTimeIn(self,numticks):
        '''
        Return the time it will be in a given number of ticks.
        
        :param numticks: The number of ticks of interest.
        
        
          called here                                                          
               |                                                    period     
               V                                                 <---------->  
        -----------------------------------------------------------------------
          |          |          |          |          |          |          |  
        -----------------------------------------------------------------------
          ^          ^          ^          ^                                   
          |          |          |          |                                   
          +----------+----------+--------- +                                   
                  numticks ticks                                               
          ^                                ^                                   
          |                                |                                   
     timeLastTick                       returned value                         
        
        :returns: The time it will be in a given number of ticks.
        '''
        
        # make sure crystal has been started
        assert self.tsTick is not None
        assert numticks>=0
        
        timeLastTick         = self.getTimeLastTick()
        period               = self._getPeriod()
        
        return timeLastTick+numticks*period
    
    def getTicksSince(self,eventTime):
        '''
        Return the number of ticks since some timestamp.
        
        :param eventTime: The time of the event of interest.
        
           eventTime                                   currentTime              
               |                                           |        period     
               V                                           V     <---------->  
        -----------------------------------------------------------------------
          |          |          |          |          |          |          |  
        -----------------------------------------------------------------------
                                                      ^                        
                                                      |                        
                                                 timeLastTick                  
                     ^          ^          ^          ^                        
                     |          |          |          |                        
                     +----------+----------+----------+                        
                          
        :returns: The number of ticks since the time passed.
        '''
        
        # make sure crystal has been started
        assert self.tsTick is not None

        # get the current time
        currentTime          = self.timeline.getCurrentTime()
        
        # make sure that eventTime passed is in the past
        assert(eventTime<=currentTime)
        
        # get the time of the last tick
        timeLastTick         = self.getTimeLastTick()
        
        # return the number of ticks
        if timeLastTick<eventTime:
            returnVal = 0
        else:
            period           = self._getPeriod()
            returnVal        = int(float(timeLastTick-eventTime)/float(period))
        
        return returnVal
    
    #======================== private =========================================
    
    def _getPeriod(self):
        
        if self._period is None:
            self._period  = float(1)/float(self.frequency)                     # nominal period
            self._period += float(self.drift/1000000.0)*float(self._period)    # apply drift
        
        return self._period
