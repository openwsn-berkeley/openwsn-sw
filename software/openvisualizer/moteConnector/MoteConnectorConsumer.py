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
        
        # local variables
        self.goOn = True
        
        # register with moteConnector
        self.moteConnector.register([self.moteConnector.TYPE_STATUS],
                                    self.notifCallback)
    
    def run(self):
        # log
        log.debug("starting to run")
    
        while self.goOn:
            print "poipoipoi"
    
    #======================== public ==========================================
    
    #======================== private =========================================