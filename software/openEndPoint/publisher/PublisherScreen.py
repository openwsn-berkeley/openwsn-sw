import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublisherScreen')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Publisher

class PublisherScreen(Publisher.Publisher):
    
    #======================== public ==========================================
    
    def publish(self,data):
        print data
    
    #======================== private =========================================