import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('EndPoint')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import ListenerEngine
import ProcessingEngine
import PublishingEngine

class EndPoint(object):
    
    def __init__(self,listener,parser,publishers):
        
        # store params
        self.listenerEngine       = None
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
            self.publishers.append(tempEngine)
            input_functions.append(tempEngine.indicateData)
        
        # processingEngine
        self.processingEngine = ProcessingEngine.ProcessingEngine(self.parser,
                                                                  input_functions)
        
        # listeningEngine
        self.listenerEngine = ListenerEngine.ListenerEngine(self.listener,
                                                            self.processingEngine.indicateData)
        
    def start(self):
    
        # log
        log.debug('starting')
    
        for pub in self.publisherEngines:
            pub.start()
        self.processingEngine.start()
        self.listenerEngine.start()
    
    def stop(self):
        # close the listening thread. This will propagate to the processing
        # and publishing threads.
        self.listenerEngine.stop()