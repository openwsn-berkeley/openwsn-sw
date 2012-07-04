
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
        output  = []
        output += ['0x']
        output += [''.join(["%.2x"%b for b in self.asn])]
        return ''.join(output)
    
    #======================== public ==========================================
    
    def update(self,byte0_1,byte2_3,byte4):
        self.asn =  [
                        byte0_1>>8,
                        byte0_1%256,
                        byte2_3>>8,
                        byte2_3%256,
                        byte4,
                    ]
    
    #======================== private =========================================
    