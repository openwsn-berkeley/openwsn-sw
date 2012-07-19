import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('InjectorCoapLed')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import InjectorCoap

class InjectorCoapLed(InjectorCoap.InjectorCoap):
    
    resources = ['l']
    
    #======================== public ==========================================
    
    @classmethod
    def inject_internal(self,destination=None,coapResource=None,fields=None):
        
        # turn fields into payload
        payload = [0x01,0x02] # poipoi
        
        # hand over to CoAP injector
        InjectorCoap.InjectorCoap.inject_internal(destination,coapResource,self.PUT,payload)
    
    #======================== private =========================================