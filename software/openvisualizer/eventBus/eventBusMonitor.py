import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('eventBusMonitor')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import copy
import json

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
        
        # get a copy of stats
        with self.statsLock:
            tempStats = copy.deepcopy(self.stats)
        
        # format as a dictionnary
        returnVal = [
            {
                'sender': str(k[0]),
                'signal': str(k[1]),
                'num':    v,
            } for (k,v) in tempStats.items()
        ]
        
        # send back JSON string
        return json.dumps(returnVal)
    
    #======================== private =========================================
    
    def _eventBusNotification(self,signal,sender,data):
        
        with self.statsLock:
            key = (sender,signal)
            if key not in self.stats:
                self.stats[key] = 0
            self.stats[key] += 1
    