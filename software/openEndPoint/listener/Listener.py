import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Listener')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Listener(object):
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.goOn       = True
    
    #======================== public ==========================================
    
    def getData(self):
        raise NotImplementedError()
    
    def stop(self):
        raise NotImplementedError()
    
    #======================== private =========================================