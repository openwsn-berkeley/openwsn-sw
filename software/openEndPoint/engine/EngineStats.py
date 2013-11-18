import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('EngineStats')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import copy

class EngineStats(object) :
    
    def __init__(self, statNames):
        
        # store params
        self.statNames = statNames
        
        # local variables
        self.statsLock = threading.Lock()
        self.stats     = {}
        
        # reset stats
        self.reset()
    
    def __str__(self):
        return '\n'.join(["- {0}: {1}".format(k,v) for (k,v) in self.stats.items()])
    
    #======================== public ==========================================
    
    def reset(self):
        self.statsLock.acquire()
        self.stats     = {}
        for name in self.statNames:
            self.stats[name] = 0
        self.statsLock.release()
    
    def increment(self,statName,step=1):
        self.statsLock.acquire()
        self.stats[statName] += step
        self.statsLock.release()
    
    def getStats(self):
        self.statsLock.acquire()
        returnVal = copy.deepcopy(self.stats)
        self.statsLock.release()
        
        return returnVal
    
    #======================== private =========================================