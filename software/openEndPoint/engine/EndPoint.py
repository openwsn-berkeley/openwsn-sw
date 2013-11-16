import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('EndPoint')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import ListeningEngine
import ProcessingEngine
import PublishingEngine

class EndPoint(object):
    
    def __init__(self,listener,parser,publishers):
        
        # store params
        self.listeningEngine      = None
        self.listener             = listener
        self.processingEngine     = None
        self.parser               = parser
        self.publisherEngines     = []
        self.publishers           = publishers
        
        # log
        log.debug('creating instance')
        
        # publisherEngines
        input_functions = []
        for publisher in self.publishers:
            tempEngine = PublishingEngine.PublishingEngine(publisher)
            self.publisherEngines.append(tempEngine)
            input_functions.append(tempEngine.indicateData)
        
        # processingEngine
        self.processingEngine = ProcessingEngine.ProcessingEngine(self.parser,
                                                                  input_functions)
        
        # listeningEngine
        self.listeningEngine = ListeningEngine.ListeningEngine(self.listener,
                                                              self.processingEngine.indicateData)
        
    def start(self):
    
        # log
        log.debug('starting')
    
        for pub in self.publisherEngines:
            pub.start()
        self.processingEngine.start()
        self.listeningEngine.start()
    
    def stop(self):
        # close the listening thread. This will propagate to the processing
        # and publishing threads.
        self.listeningEngine.stop()
    
    def getStats(self):
        return  {
            'listeningEngine'     : self.listeningEngine.getStats(),
            'processingEngine'    : self.processingEngine.getStats(),
            'publisherEngines'    : [pub.getStats() for pub in self.publisherEngines],
        }