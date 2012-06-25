
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserStatus')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from ParserException import ParserException
import Parser

class ParserStatus(Parser.Parser):
    
    MIN_LENGTH = 4
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.MIN_LENGTH)
    
    #======================== public ==========================================
    
    #======================== private =========================================