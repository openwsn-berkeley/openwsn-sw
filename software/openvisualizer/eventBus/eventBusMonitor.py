import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('eventBusMonitor')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

from pydispatch import dispatcher

class eventBusMonitor(object):
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # local variables
        self.statsLock  = threading.Lock()
        self.stats      = {}
        
        # give this instance a name
        self.name       = 'eventBusMonitor'
        
        # connect to dispatcher
        dispatcher.connect(
            self._eventBusNotification,
        )
    
    #======================== public ==========================================
    
    def getStats(self):
        with self.statsLock:
            return copy.deepcopy(self.stats)
    
    #======================== private =========================================
    
    def _eventBusNotification(self,signal,sender,data):
        
        with self.statsLock:
            key = (signal,sender)
            if key not in self.stats:
                self.stats[key] = 0
            self.stats[key] += 1
    