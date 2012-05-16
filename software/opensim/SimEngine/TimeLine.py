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
        '''
        \brief Add an event into the timeline
        
        \param atTime The time at which this event should be called.
        \param cd     The function to call when this event happens.
        \param desc   A unique description (a string) of this event.
        '''
        
        # log
        self.log.debug('scheduling '+desc+' at '+str(atTime))
        
        # make sure that I'm scheduling an event in the future
        assert(self.currentTime<=atTime)
        
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
        self.timeline.insert(i-1,newEvent)
        
    def cancelEvent(self,desc):
        '''
        \brief Cancels all events identified by their description
        
        \param desc   A unique description (a string) of this event.
        
        \returns The number of events canceled.
        '''
        
        # log
        self.log.debug('cancelEvent '+desc)
        
        # initialize return variable
        numEventsCanceled = 0
        
        # remove any event already the queue with same description
        i = 0
        while i<len(self.timeline):
            if self.timeline[i].desc==desc:
                self.timeline.pop(i)
                numEventsCanceled += 1
            else:
                i += 1
        
        # return the number of events canceled
        return numEventsCanceled
    
    def nextEvent(self):
        '''
        \brief Advance in the queue of events.
        '''
        
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
        self.log.debug('executing event '+str(event.desc)+' at '+str(event.atTime))
        
        # call the event's callback
        event.cb()
    
    #======================== private =========================================
    
    def _printTimeline(self):
        output  = ''
        for event in self.timeline:
            output += '\n'+str(event.atTime)+' '+str(event.desc)
        return output
    
    #======================== helpers =========================================
    