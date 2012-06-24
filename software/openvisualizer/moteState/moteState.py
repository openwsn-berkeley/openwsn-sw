
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class moteState(object):
    
    def __init__(self,moteConnector):
        
        # log
        log.debug("create instance")
        
        # store params
        self.moteConnector = moteConnector
        
        # local variables
        
        # register with moteConnector
        self.moteConnector.register(self.receivedData_notif)
    
    #======================== public ==========================================
    
    def receivedData_notif(self,input):
        print input
    
    #======================== private =========================================