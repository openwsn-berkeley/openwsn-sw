import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Publisher')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Publisher(object):
    
    #======================== public ==========================================
    
    def run(self):
        pass
    
    def publish(self,timestamp,source,data):
        raise NotImplemeterError()
    
    #======================== private =========================================