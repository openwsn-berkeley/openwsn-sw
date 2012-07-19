import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Injector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Injector(object):
    
    #======================== public ==========================================
    
    @classmethod
    def inject(self,payload=None,destination=None):
        raise NotImplemeterError()
    
    #======================== private =========================================