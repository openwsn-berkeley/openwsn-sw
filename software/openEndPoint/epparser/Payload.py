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
        return self.__payload

    def setPayload(self, payload):
        self.__payload = payload      
       
    def toJSON(self):
        json=JSONWrapper.JSONWrapper()
        return json.json_repr(self)

    def __str__( self ):
       return self.toJSON(self)

    def __repr__( self ):
       return self.toJSON(self)
