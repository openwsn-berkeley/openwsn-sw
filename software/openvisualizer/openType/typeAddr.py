
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
        if self.addr:
           output += ['-'.join(["%.2x"%b for b in self.addr])]
        output += [' (']
        output += [self.desc]
        output += [')']
        return ''.join(output)
    
    #======================== public ==========================================
    
    def update(self,type,bodyH,bodyL):
        fullAddr = [
                        bodyH>>(4*7) & 0xff,
                        bodyH>>(4*6) & 0xff,
                        bodyH>>(4*5) & 0xff,
                        bodyH>>(4*4) & 0xff,
                        bodyH>>(4*3) & 0xff,
                        bodyH>>(4*2) & 0xff,
                        bodyH>>(4*1) & 0xff,
                        bodyH>>(4*0) & 0xff,
                        bodyL>>(4*7) & 0xff,
                        bodyL>>(4*6) & 0xff,
                        bodyL>>(4*5) & 0xff,
                        bodyL>>(4*4) & 0xff,
                        bodyL>>(4*3) & 0xff,
                        bodyL>>(4*2) & 0xff,
                        bodyL>>(4*1) & 0xff,
                        bodyL>>(4*0) & 0xff,
                   ]
        self.type = type
        if   type==self.ADDR_NONE:
            self.desc = 'None'
            self.addr = None
        elif type==self.ADDR_16B:
            self.desc = '16b'
            self.addr = [fullAddr[7],fullAddr[5]]
        elif type==self.ADDR_64B:
            self.desc = '64b'
            self.addr = fullAddr
        elif type==self.ADDR_128B:
            self.desc = '128b'
            self.addr = fullAddr
        elif type==self.ADDR_PANID:
            self.desc = 'panId'
            self.addr = [fullAddr[7],fullAddr[5]]
        elif type==self.ADDR_PREFIX:
            self.desc = 'prefix'
            self.addr = fullAddr[:8]
        elif type==self.ADDR_ANYCAST:
            self.desc = 'anycast'
            self.addr = None
        else:
            self.desc = 'unknown'
            self.addr = None
    
    #======================== private =========================================
    