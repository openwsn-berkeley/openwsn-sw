import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NeighborsParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import SpecificParser
import CoapHeader
import Payload

# Parses the neighbours payload.
class NeighborsParser(SpecificParser.SpecificParser):
    
    apps=['ld_n']   #application name, can be a list.    
    #======================== public ==========================================
    
    def create(self,name):
       if name in apps:
          return;
       else:
          raise Error()  #check how to throw exception.

    #TODO
    def parse(self,data):
        returnVal          = {} 
        
       
        return returnVal
    
    #======================== private =========================================
