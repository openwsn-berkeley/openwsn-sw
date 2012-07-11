import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ScheduleParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import SpecificParser
import CoapHeader
import Payload


# Parses the schedule payload.
class ScheduleParser(SpecificParser.SpecificParser):
    
    apps='ld_s'   #application name, can be a list.    
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
