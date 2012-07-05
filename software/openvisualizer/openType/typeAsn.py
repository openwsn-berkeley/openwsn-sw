
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('typeAsn')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

import openType

class typeAsn(openType.openType):
    
    def __init__(self):
        # log
        log.debug("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        return '0x{0}'.format(''.join(["%.2x"%b for b in self.asn]))
    
    #======================== public ==========================================
    
    def update(self,byte0_1,byte2_3,byte4):
        self.asn =  [
                        byte4,
                        byte2_3>>8,
                        byte2_3%256,
                        byte0_1>>8,
                        byte0_1%256,
                    ]
    
    #======================== private =========================================
    