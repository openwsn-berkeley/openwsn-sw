
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('typeAddr')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

import openType

class typeAddr(openType.openType):
    
    ADDR_NONE    = 0
    ADDR_16B     = 1
    ADDR_64B     = 2
    ADDR_128B    = 3
    ADDR_PANID   = 4
    ADDR_PREFIX  = 5
    ADDR_ANYCAST = 6
    
    def __init__(self):
        # log
        log.debug("creating object")
        
        # initialize parent class
        openType.openType.__init__(self)
    
    def __str__(self):
        output  = []
        if self.addr
           output += ['-'.join(["%.2x"%b for b in self.addr])]
        output += [' (']
        output += [self.desc]
        output += [')']
        return ''.join(output)
    
    #======================== public ==========================================
    
    def update(self,type,body):
        self.type = type
        if   type==self.ADDR_NONE:
            self.desc = 'None'
            self.addr = None
        elif type==self.ADDR_16B:
            self.desc = '16b'
            self.addr = None
        elif type==self.ADDR_64B:
            self.desc = '64b'
            self.addr = None
        elif type==self.ADDR_128B:
            self.desc = '128b'
            self.addr = None
        elif type==self.ADDR_PANID:
            self.desc = 'panId'
            self.addr = None
        elif type==self.ADDR_PREFIX:
            self.desc = 'prefix'
            self.addr = None
        elif type==self.ADDR_ANYCAST:
            self.desc = 'anycast'
            self.addr = None
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    