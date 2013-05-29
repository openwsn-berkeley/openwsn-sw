#!/usr/bin/python

import logging
import threading

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

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
    \brief The timeline of the engine.
    '''
    
    def __init__(self,engine):
        
        # store params
        self.engine               = engine
        
        # local variables
        self.currentTime          = 0   # current time
        self.timeline             = []  # list of upcoming events
        self.firstEventPassed     = False
        self.firstEvent           = threading.Lock()
        self.firstEvent.acquire()
        self.moteBusy             = threading.Lock()
        self.moteBusy.acquire()
        self.stats                = TimeLineStats()
        
        # logging
        self.log                  = logging.getLogger('Timeline')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('TimeLine')
        
        # thread daemon mode
        self.setDaemon(True)
    
    def run(self):
        # log
        self.log.debug('starting')
        
        # log
        self.log.debug('waiting for first event')
        
        # wait for the first event to be scheduled
        self.firstEvent.acquire()
        self.firstEventPassed = True
        self.engine.indicateFirstEventPassed()
        
        # log
        self.log.debug('first event scheduled')
        
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
            
            # record the mote'd ID
            self.moteBusyId = event.moteId
            
            # log
            self.log.debug('\n\nnow {0:.6f}, executing {1}@{2}'.format(event.atTime,
                                                                   event.desc,
                                                                   event.moteId,))
            
            # call the event's callback
            event.cb()
            
            # wait for the mote to be done
            self.moteBusy.acquire()
            
            # update statistics
            self.stats.incrementEvents()
            
            # apply the delay
            self.engine.pauseOrDelay()
    
    #======================== public ==========================================
    
    def getCurrentTime(self):
        return self.currentTime
    
    def scheduleEvent(self,atTime,moteId,cb,desc):
        '''
        \brief Add an event into the timeline
        
        \param atTime The time at which this event should be called.
        \param cb     The function to call when this event happens.
        \param desc   A unique description (a string) of this event.
        '''
        
        # log
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
        
        # start the timeline, if applicable
        if not self.firstEventPassed:
            self.firstEvent.release()
        
    def cancelEvent(self,moteId,desc):
        '''
        \brief Cancels all events identified by their description
        
        \param desc   A unique description (a string) of this event.
        
        \returns The number of events canceled.
        '''
        
        # log
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
    
    def moteDone(self,moteId):
        
        # make sure that the mote which is done is one expected
        assert(moteId==self.moteBusyId)
        
        # post the semaphore to timeline thread can go on
        self.moteBusy.release()
    
    def getStats(self):
        return self.stats
    
    #======================== private =========================================
    
    def _printTimeline(self):
        output  = ''
        for event in self.timeline:
            output += '\n'+str(event)
        return output
    
    #======================== helpers =========================================
    