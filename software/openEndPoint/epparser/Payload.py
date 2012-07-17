import logging
import IsJSON

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Payload')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Payload(IsJSON.IsJSON):
   
    #Payload
    def getPayload(self):
        return self._payload

    def setPayload(self, payload):
        self._payload = payload      
       
    

    
