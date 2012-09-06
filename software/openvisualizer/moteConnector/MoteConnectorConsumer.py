import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnectorConsumer')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket
import Queue

from pydispatch import dispatcher

import OpenParser
import ParserException

class MoteConnectorConsumer(threading.Thread):
    
    QUEUESIZE = 100
    
    def __init__(self,signal,sender,notifCallback):
        
        # log
        log.debug("create instance")
        
        # store params
        self.notifCallback = notifCallback
        self.sender        = sender
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name          = 'MoteConnectorConsumer'
        
        # local variables
        self.goOn          = True
        self.dataQueue     = Queue.Queue(self.QUEUESIZE)
        
        # connect to dispatcher
        dispatcher.connect(
            self._eventBusNotification,
            signal = signal,
        )
        
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
    
    def _eventBusNotification(self,signal,sender,data):
        
        if (self.sender!=dispatcher.Any) and (sender!=self.sender):
            return
        
        if self.dataQueue.full():
            raise SystemError("Queue is full")
        
        self.dataQueue.put(data)