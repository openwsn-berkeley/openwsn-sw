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
        
        if   isinstance(data, dict):
            print "{2} from {1} at {0}".format(self._formatTimestamp(timestamp),
                                               source,
                                               '\n'.join(["{0}:{1}".format(k,v) for (k,v) in data.items()]))
        elif isinstance(data, (list,tuple)):
            print "{2} from {1} at {0}".format(self._formatTimestamp(timestamp),
                                               source,
                                               ''.join(["%.2x"%b for b in data]))
        else:
            print "{2} from {1} at {0}".format(self._formatTimestamp(timestamp),
                                               source,
                                               data)
        
        file = open("poipoi.txt","a")
        file.write(' '.join(["%.2x"%b for b in data]) + '\n')
        file.close()
    
    #======================== private =========================================
    
    def _formatTimestamp(self,timestamp):
        return time.strftime(self.FORMAT_TIMESTAMP,time.localtime(timestamp))
