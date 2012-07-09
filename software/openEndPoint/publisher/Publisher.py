import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Publisher')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Publisher(object):
    
    #======================== public ==========================================
    
    def publish(self,data):
        raise NotImplemeterError()
    
    #======================== private =========================================