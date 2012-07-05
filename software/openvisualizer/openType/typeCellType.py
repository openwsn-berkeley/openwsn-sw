
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('typeCellType')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

import openType

class typeCellType(openType.openType):
    
    CELLTYPE_OFF             = 0
    CELLTYPE_ADV             = 1
    CELLTYPE_TX              = 2
    CELLTYPE_RX              = 3
    CELLTYPE_TXRX            = 4
    CELLTYPE_SERIALRX        = 5
    CELLTYPE_MORESERIALRX    = 6
    
    def __init__(self):
        # log
        log.debug("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        output  = []
        output += [str(self.type)]
        output += [' (']
        output += [self.desc]
        output += [')']
        return ''.join(output)
    
    #======================== public ==========================================
    
    def update(self,type):
        self.type = type
        if   type==self.CELLTYPE_OFF:
            self.desc = 'OFF'
        elif type==self.CELLTYPE_ADV:
            self.desc = 'ADV'
        elif type==self.CELLTYPE_TX:
            self.desc = 'TX'
        elif type==self.CELLTYPE_RX:
            self.desc = 'RX'
        elif type==self.CELLTYPE_TXRX:
            self.desc = 'TXRX'
        elif type==self.CELLTYPE_SERIALRX:
            self.desc = 'SERIALRX'
        elif type==self.CELLTYPE_MORESERIALRX:
            self.desc = 'MORESERIALRX'
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    