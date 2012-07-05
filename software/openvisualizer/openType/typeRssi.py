
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('typeRssi')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

import openType

class typeRssi(openType.openType):
    
    def __init__(self):
        # log
        log.debug("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        return '{0}dBm'.format(self.rssi)
    
    #======================== public ==========================================
    
    def update(self,rssi):
        self.rssi = rssi
    
    #======================== private =========================================
    