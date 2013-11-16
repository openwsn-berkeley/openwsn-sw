import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ProcessingEngine')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import Queue

import EngineStats
from   EngineException import OutputUnavailableException,  \
                              ParsingException

class ProcessingEngine(threading.Thread):
    
    def __init__(self,parser,output_cbs):
        
        # store params
        self.parser     = parser
        self.output_cbs = output_cbs
        
        # log
        log.debug("creating instance")
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'ProcessingEngine'
        
        # local variables
        self.goOn       = True
        self.inputQueue = Queue.Queue()
        self.stats      = EngineStats.EngineStats(['numIn',
                                                   'numParseOk',
                                                   'numParseFail',
                                                   'numOutOk',
                                                   'numOutFail'])
    
    def run(self):
        
        # log
        log.debug('starting')
        
        while self.goOn:
            
            # block until reading data from the input queue
            (timestamp,source,data) = self.inputQueue.get()
            
            # increment stats
            self.stats.increment('numIn')
            
            # parse
            try:
                parsedData = self.parser.parse(data)
            except ParsingException:
                # increment stats
                self.stats.increment('numParseFail')
            else:
                # increment stats
                self.stats.increment('numParseOk')
                
                # call the callbacks
                for cb in self.output_cbs:
                    cb((timestamp,source,parsedData))
    
    #======================== public ==========================================
    
    def indicateData(self,data):
        try:
            self.inputQueue.put_nowait(data)
        except Queue.Full:
            raise OutputUnavailableException()
    
    def getStats(self):
        return self.stats.getStats()
    
    #======================== private =========================================