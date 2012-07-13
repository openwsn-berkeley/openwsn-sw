import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NeighborsParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import SpecificParser
import Payload


# Parses the schedule payload.
class NeighborsParser(SpecificParser.SpecificParser):
    
    apps=['ld_n']   #application name, can be a list.
    headerStructure = {
        'structure': '<HbBBH', # little-endian, 2byte,1Byte signed,2 one-byte fields,2byte field
        'fieldNames': ['address','rssi','parentPref','DAGRank','ASN',],
        'repeat':     True,
    }
    
    #======================== public ==========================================
    
    def create(self,name):
       if name not in apps:
         raise IncorrectParserException('the specified app cannot be parsed by NeighborsParser. Try another parser.')  #check how to throw exception.
    
    #======================== private =========================================
        