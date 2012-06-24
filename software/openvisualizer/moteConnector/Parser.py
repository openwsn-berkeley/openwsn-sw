
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Parser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from ParserException import ParserException

class Parser(object):
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # local variables
        
        # register with moteConnector
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        return ParserException(ParserException.GENERIC)
    
    #======================== private =========================================