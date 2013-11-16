'''
Created on 17/07/2012

@author: xvilajosana
'''
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('UDPStormParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import SpecificParser
from .. import CoapHeader
from .. import Payload


from ..ParserException import IncorrectParserException

# Parses the ures test data
class UDPStormParser(SpecificParser.SpecificParser):
    
    apps=['strm']   #application name, can be a list.
    headerStructure = {
        'structure': '<H', # little-endian, 
        'fieldNames': ['sequence'],
        'repeat':     False,
    }
    
    #======================== public ==========================================
    
    def create(self,name):
       if name not in self.apps:
            raise IncorrectParserException('the specified app cannot be parsed by UDPStormParser. Try another parser.')  #check how to throw exception.
    
    #======================== private =========================================
    
    def parse(self, data):
       return SpecificParser.SpecificParser.parse(self,data)