
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('openType')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

class openType(object):
    
    def __init__(self):
        # log
        log.info("creating object")
        
        self.initialized = None
    
    #======================== public ==========================================
    
    def initFromBytes(self,byteArray):
        raise NotImplementedError
    
    def initFromFields(self,fields):
        raise NotImplementedError
    
    #======================== private =========================================
    