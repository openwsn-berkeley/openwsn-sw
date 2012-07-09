import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Parser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Parser(object):
    
    #======================== public ==========================================
    
    def parse(self):
        raise NotImplemeterError()
    
    #======================== private =========================================