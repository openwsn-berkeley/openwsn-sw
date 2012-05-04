#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

        
class TimeLineEvent(object):
    
    def __init__(self,atTime,cb,desc):
        self.atTime     = atTime
        self.cb         = cb
        self.desc       = desc
    
class TimeLine(object):
    '''
    \brief The timeline of the engine.
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.currentTime          = 0   # current time
        self.timeline             = []  # list of upcoming events
        
        # logging
        self.log                  = logging.getLogger('Timeline')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
    
    #======================== public ==========================================
    
    def getCurrentTime(self):
        return self.currentTime
    
    def scheduleEvent(self,atTime,cb,desc):
        
        # log
        self.log.debug('scheduling '+desc+' at '+str(atTime))
        
        # create a new event
        newEvent = TimeLineEvent(atTime,cb,desc)
        
        # remove any event already the queue with same description
        for i in range(len(self.timeline)):
            if self.timeline[i].desc==desc:
                self.timeline.pop(i)
                break
        
        # look for where to put this event
        i = 0
        while i<len(self.timeline) and newEvent.atTime<self.timeline[i].atTime:
            i += 1
        
        # insert the new event
        self.timeline.insert(i,newEvent)
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    