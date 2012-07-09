import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublisherScreen')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class PublisherScreen(object):
    
    #======================== public ==========================================
    
    def publish(self,data):
        print data
    
    #======================== private =========================================