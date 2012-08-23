import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('networkState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import RPL

from moteConnector import MoteConnectorConsumer

class networkState(MoteConnectorConsumer.MoteConnectorConsumer):
    
    def __init__(self,moteConnector):
        
        # log
        log.debug("create instance")
        
        # store params
        self.moteConnector                  = moteConnector
        
        # initialize parent class
        MoteConnectorConsumer.MoteConnectorConsumer.__init__(self,self.moteConnector,
                                                                  [self.moteConnector.TYPE_DATA_LOCAL],
                                                                  self._receivedData_notif)
        
        # local variables
        self.stateLock                      = threading.Lock()
        self.state                          = {}
        self.rpl                            = RPL.RPL()
        self.rpl.test()
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _receivedData_notif(self,notif):
        
        # log
        log.debug("received {0}".format(notif))
        
        # indicate data to RPL
        self.rpl.update(notif)