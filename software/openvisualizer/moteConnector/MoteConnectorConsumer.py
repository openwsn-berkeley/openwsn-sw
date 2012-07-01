import threading
import socket

import OpenParser
import ParserException

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnectorConsumer')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class MoteConnectorConsumer(threading.Thread):
    
    def __init__(self,moteConnector,dataType,notifCallback):
        
        # log
        log.debug("create instance")
        
        # store params
        self.moteConnector = moteConnector
        self.dataType      = dataType
        self.notifCallback = notifCallback
        self.dataQueue     = self.moteConnector.register(
                                self.dataType,
                             )
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name          = 'MoteConnectorConsumer'
        
        # local variables
        self.goOn = True
    
    def run(self):
        # log
        log.debug("starting to run")
    
        while self.goOn:
        
            # get data from the queue
            newData = self.dataQueue.get()
            
            # log
            log.debug("got data: {0}".format(newData))
            
            # call the callback
            self.notifCallback(newData)
    
    #======================== public ==========================================
    
    #======================== private =========================================