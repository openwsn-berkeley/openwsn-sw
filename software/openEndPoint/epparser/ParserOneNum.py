import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserOneNum')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Parser

class ParserOneNum(Parser.Parser):
    
    #======================== public ==========================================
    
    def parse(self,data):
        returnVal          = {}
        returnVal['value'] = 0
        for i in range(len(data)):
            returnVal['value'] += data[i]<<(8*(len(data)-1-i))
        
        '''
        print "{0} --> {1}".format([hex(b) for b in data],
                                    hex(returnVal['value']))
        '''
        
        return returnVal
    
    #======================== private =========================================