import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('InjectorCoap')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import random

import InjectorUdp
from InjectorException import NoSuitableInjectorException

class InjectorCoap(InjectorUdp.InjectorUdp):
    
    CONFIRMABLE   = 0
    
    VERSION       = 1
    
    TYPE_URI_PATH = 9
    
    POST          = 2
    PUT           = 3
    
    resources = []
    
    #======================== public ==========================================
    
    @classmethod
    def inject(self,destination=None,coapResource=None,fields=None):
        print self.__subclasses__()
        for injector in self.__subclasses__():
            if coapResource in injector.resources:
                injector.inject_internal(destination,coapResource,fields)
                return
        raise NoSuitableInjectorException()
    
    @classmethod
    def inject_internal(self,destination=None,coapResource=None,method=None,payload=None):
        
        assert(method in [self.POST,self.PUT])
        
        #=== CoAP options
        coapOptions = []
        
        uriPath     = []
        uriPath    += [self.TYPE_URI_PATH<<4 | len(coapResource)]
        uriPath    += [ord(b) for b in coapResource]
        coapOptions.append(uriPath)
        
        #=== CoAP header
        coapHeader  = []
        coapHeader += [
                        self.VERSION<<6     |
                        self.CONFIRMABLE<<4 |
                        len(coapOptions)<<0
                      ]
        coapHeader += [method]
        coapHeader += [random.randint(0,255),random.randint(0,255)]
        
        # build final payload
        payload     = coapHeader + sum(coapOptions,[]) + payload
        
        # hand over to UDP injector
        InjectorUdp.InjectorUdp.inject(destination,payload)
    
    #======================== private =========================================