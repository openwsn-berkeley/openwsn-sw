import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserOneNum')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Parser

class ParserOneList(Parser.Parser):
    
    #======================== public ==========================================
    
    def parse(self,data):
        returnVal          = data[:]
        
        return returnVal
    
    #======================== private =========================================