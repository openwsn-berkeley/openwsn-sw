import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SpecificParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#interface implemented by specific parsers. Implement that interface if you want to parse an specific payload.
class SpecificParser(object):
    
    #======================== public ==========================================
    
    #returns if name matches to the name defined in the implementing class. If not throws an exception.
    def create(self, name):
        raise NotImplemeterError()

    def parse(self):
        raise NotImplemeterError()
    
    #======================== private =========================================
