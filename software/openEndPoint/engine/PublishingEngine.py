import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublishingEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import Queue

import EngineStats
from   EngineException import OutputUnavailableException

class PublishingEngine(threading.Thread):
    
    def __init__(self,publisher):
        
        # store params
        self.publisher  = publisher
        
        # log
        log.debug("creating instance")
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'PublishingEngine'
        
        # local variables
        self.goOn       = True
        self.inputQueue = Queue.Queue()
        self.stats      = EngineStats.EngineStats(['numIn',
                                                   'numPublishedOk',
                                                   'numPublishedFail'])
    
    def run(self):
        
        # log
        log.debug('starting')
        
        while self.goOn:
            
            # block until reading data from the input queue
            data = self.inputQueue.get()
            
            # increment stats
            self.stats.increment('numIn')
            
            # publish
            try:
                self.publisher.publish()
            except PublishingException:
                # increment stats
                self.stats.increment('numPublishedFail')
            else:
                # increment stats
                self.stats.increment('numPublishedOk')
    
    #======================== public ==========================================
    
    def indicateData(self,data):
        try:
            self.inputQueue.put_nowait(data)
        except Queue.Full:
            raise OutputUnavailableException()
    
    #======================== private =========================================