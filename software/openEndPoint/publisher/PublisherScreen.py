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
    
    def publish(self,timestamp,source,data):
        print "{2} from {1} at {0}".format(timestamp,source,data)
    
    #======================== private =========================================