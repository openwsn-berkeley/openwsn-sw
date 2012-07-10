import logging
import JSONWrapper

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Payload')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Payload:
   
    #Payload
    def getPayload(self):
        return self._payload

    def setPayload(self, payload):
        self._payload = payload      
       
    def toJSON(self):
        json=JSONWrapper.JSONWrapper()
        return json.json_repr(self)

    def __str__( self ):
       return self.toJSON()

    
