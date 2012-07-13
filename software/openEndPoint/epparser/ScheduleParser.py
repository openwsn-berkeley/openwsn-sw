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
    
    apps=['d_s']   #application name, can be a list.
    headerStructure = {
        'structure': '<BBB', # little-endian, 3 one-byte fields
        'fieldNames': ['address','slotOffset','channelOffset'],
        'repeat':     True,
    }
    
    #======================== public ==========================================
    
    def create(self,name):
       if name not in apps:
            raise IncorrectParserException('the specified app cannot be parsed by ScheduleParser. Try another parser.')  #check how to throw exception.
    
    #======================== private =========================================
    
    def parse(self, data):
       SpecificParser.SpecificParser.parse(self,data)