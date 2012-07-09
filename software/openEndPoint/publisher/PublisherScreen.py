import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublisherScreen')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time

import Publisher

class PublisherScreen(Publisher.Publisher):
    
    FORMAT_TIMESTAMP = '%Y/%m/%d %H:%M:%S'
    
    #======================== public ==========================================
    
    def publish(self,timestamp,source,data):
        print "{2} from {1} at {0}".format(self._formatTimestamp(timestamp),
                                           source,
                                           data)
    
    #======================== private =========================================
    
    def _formatTimestamp(self,timestamp):
        return time.strftime(self.FORMAT_TIMESTAMP,time.localtime(timestamp))