
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserData')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import struct

from ParserException import ParserException
import Parser

class ParserData(Parser.Parser):
    
    HEADER_LENGTH = 2
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # log
        log.debug("received data {0}".format(input))
        
        # ensure input not short longer than header
        self._checkLength(input)
        
        headerBytes = input[:2]
        
        # extract moteId and statusElem
        try:
           (moteId) = struct.unpack('<H',''.join([chr(c) for c in headerBytes]))
        except struct.error:
            raise ParserException(ParserException.DESERIALIZE,"could not extract moteId from {0}".format(headerBytes))
        
        # log
        log.debug("moteId={0}".format(moteId))
        
        # jump the header bytes
        input = input[2:]
        
        return input
    
    #======================== private =========================================