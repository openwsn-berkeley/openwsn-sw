#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass
        
class TimeLineEvent(object):
    
    def __init__(self,moteId,atTime,cb,desc):
        self.moteId     = moteId
        self.atTime     = atTime
        self.cb         = cb
        self.desc       = desc
    
    def __str__(self):
        return '{0} {1}: {2}'.format(self.atTime,self.moteId,self.desc)
    
class TimeLine(object):
    '''
    \brief The timeline of the engine.
    '''
    
    def __init__(self,engine):
        
        # store params
        self.engine               = engine
        
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
    
    def scheduleEvent(self,atTime,moteId,cb,desc):
        '''
        \brief Add an event into the timeline
        
        \param atTime The time at which this event should be called.
        \param cd     The function to call when this event happens.
        \param desc   A unique description (a string) of this event.
        '''
        
        # log
        self.log.debug('scheduling {0} at {1:.6f}'.format(desc,atTime))
        
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
        
        # remove any event already the queue with same description
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
        
    def cancelEvent(self,moteId,desc):
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
    
    def nextEvent(self):
        '''
        \brief Advance in the queue of events.
        '''
        
        goOn = True
        
        while goOn:
        
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
            self.log.debug('executing {0} at {1:.6f}'.format(event.desc,event.atTime))
            
            # call the event's callback
            goOn = event.cb()
        
    def getEvents(self):
        return [[ev.atTime,ev.moteId,ev.desc] for ev in self.timeline]
    
    #======================== private =========================================
    
    def _printTimeline(self):
        output  = ''
        for event in self.timeline:
            output += '\n'+str(event)
        return output
    
    #======================== helpers =========================================
    