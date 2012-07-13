import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ScheduleParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import SpecificParser
from .. import CoapHeader
from .. import Payload
#from .. import IncorrectParserException

from ..ParserException import IncorrectParserException

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
       if name not in self.apps:
            raise IncorrectParserException('the specified app cannot be parsed by ScheduleParser. Try another parser.')  #check how to throw exception.
    
    #======================== private =========================================
    
    def parse(self, data):
       return SpecificParser.SpecificParser.parse(self,data)