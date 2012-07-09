import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserOneNum')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class ParserOneNum(object):
    
    #======================== public ==========================================
    
    def parse(self,data):
        returnVal              = {}
        returnVal['valString'] = '0x{0}'.format(''.join(["%.2x"%b for b in data]))
        
        return returnVal
    
    #======================== private =========================================