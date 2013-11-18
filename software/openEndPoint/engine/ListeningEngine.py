import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ListeningEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

import EngineStats
from   EngineException import TearDownException,           \
                              OutputUnavailableException

class ListeningEngine(threading.Thread):
    
    def __init__(self,listener,output_cb):
        
        # store params
        self.listener   = listener
        self.output_cb  = output_cb
        
        # log
        log.debug("creating instance")
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name       = 'ListeningEngine'
        
        # local variables
        self.stats      = EngineStats.EngineStats(['numIn',
                                                   'numOutOk',
                                                   'numOutFail'])
    
    #======================== public ==========================================
    
    def run(self):
        
        while True:
            
            # block until receiving some data
            try:
                (timestamp,source,data) = self.listener.getData()
            except TearDownException:
                # log
                self.warning("TearDown")
                
                # stop this thread
                break
            
            # log
            log.debug("Got data {2} at {0} from {1}".format(timestamp,source,data))
            
            # update stats
            self.stats.increment('numIn')
            
            # pass on to output
            try:
                self.output_cb((timestamp,source,data))
            except OutputUnavailableException:
                self.stats.increment('numOutFail')
            else:
                self.stats.increment('numOutOk')
    
    def stop(self):
        self.listener.stop()
    
    def getStats(self):
        return self.stats.getStats()
    
    #======================== private =========================================