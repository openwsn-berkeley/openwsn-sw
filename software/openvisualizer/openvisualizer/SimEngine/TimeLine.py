#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging
import threading

import SimEngine

class TimeLineStats(object):
    
    def __init__(self):
        self.numEvents  = 0
        
    def incrementEvents(self):
        self.numEvents += 1
    
    def getNumEvents(self):
        return self.numEvents
        
class TimeLineEvent(object):
    
    def __init__(self,moteId,atTime,cb,desc):
        self.atTime     = atTime
        self.moteId     = moteId
        self.desc       = desc
        self.cb         = cb
    
    def __str__(self):
        return '{0} {1}: {2}'.format(self.atTime,self.moteId,self.desc)
    
class TimeLine(threading.Thread):
    '''
    The timeline of the engine.
    '''
    
    def __init__(self):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        
        # local variables
        self.currentTime          = 0   # current time
        self.timeline             = []  # list of upcoming events
        self.firstEventPassed     = False
        self.firstEvent           = threading.Lock()
        self.firstEvent.acquire()
        self.firstEventLock       = threading.Lock()
        self.stats                = TimeLineStats()
        
        # logging
        self.log                  = logging.getLogger('Timeline')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('TimeLine')
        
        # thread daemon mode
        self.setDaemon(True)
    
    def run(self):
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('starting')
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('waiting for first event')
        
        # wait for the first event to be scheduled
        self.firstEvent.acquire()
        self.engine.indicateFirstEventPassed()
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('first event scheduled')
        
        # apply the delay
        self.engine.pauseOrDelay()
        
        while True:
            
            # detect the end of the simulation
            if len(self.timeline)==0:
                output  = ''
                output += 'end of simulation reached\n'
                output += ' - currentTime='+str(self.getCurrentTime())+'\n'
                self.log.warning(output)
                raise StopIteration(output)
            
            # pop the event at the head of the timeline
            event = self.timeline.pop(0)
            
            # make sure that this event is later in time than the previous
            assert(self.currentTime<=event.atTime)
            
            # record the current time
            self.currentTime = event.atTime
            
            # log
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('\n\nnow {0:.6f}, executing {1}@{2}'.format(event.atTime,
                                                                       event.desc,
                                                                       event.moteId,))
            
            # call the event's callback
            self.engine.getMoteHandlerById(event.moteId).handleEvent(event.cb)
            
            # update statistics
            self.stats.incrementEvents()
            
            # apply the delay
            self.engine.pauseOrDelay()
    
    #======================== public ==========================================
    
    def getCurrentTime(self):
        return self.currentTime
    
    def scheduleEvent(self,atTime,moteId,cb,desc):
        '''
        Add an event into the timeline
        
        :param atTime: The time at which this event should be called.
        :param cb:     The function to call when this event happens.
        :param desc:   A unique description (a string) of this event.
        '''
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('scheduling {0}@{1} at {2:.6f}'.format(desc,moteId,atTime))
        
        # make sure that I'm scheduling an event in the future
        try:
            assert(self.currentTime<=atTime)
        except AssertionError:
            self.engine.pause()
            print "currentTime: "+str(self.currentTime)
            print "atTime:      "+str(atTime)
            print "moteId:      "+str(moteId)
            print "desc:        "+str(desc)
            raise
        
        # create a new event
        newEvent = TimeLineEvent(moteId,atTime,cb,desc)
        
        # remove any event already in the queue with same description
        for i in range(len(self.timeline)):
            if (self.timeline[i].moteId==moteId and
                self.timeline[i].desc==desc):
                self.timeline.pop(i)
                break
        
        # look for where to put this event
        i = 0
        while i<len(self.timeline):
            if newEvent.atTime>self.timeline[i].atTime:
               i += 1
            else:
               break
        
        # insert the new event
        self.timeline.insert(i,newEvent)
        
        # start the timeline, if applicable
        with self.firstEventLock:
            if not self.firstEventPassed:
                self.firstEventPassed = True
                self.firstEvent.release()
        
    def cancelEvent(self,moteId,desc):
        '''
        Cancels all events identified by their description
        
        :param desc: A unique description (a string) of this event.
        
        :returns:    The number of events canceled.
        '''
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cancelEvent {0}@{1}'.format(desc,moteId))
        
        # initialize return variable
        numEventsCanceled = 0
        
        # remove any event already the queue with same description
        i = 0
        while i<len(self.timeline):
            if (
                  self.timeline[i].moteId==moteId and
                  self.timeline[i].desc==desc
               ):
                self.timeline.pop(i)
                numEventsCanceled += 1
            else:
                i += 1
        
        # return the number of events canceled
        return numEventsCanceled
        
    def getEvents(self):
        return [[ev.atTime,ev.moteId,ev.desc] for ev in self.timeline]
    
    def getStats(self):
        return self.stats
    
    #======================== private =========================================
    
    def _printTimeline(self):
        output  = ''
        for event in self.timeline:
            output += '\n'+str(event)
        return output
    
    #======================== helpers =========================================
    