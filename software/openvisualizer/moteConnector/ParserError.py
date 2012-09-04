
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserError')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import struct

from ParserException import ParserException
import Parser

import StackDefines

class ParserError(Parser.Parser):
    
    HEADER_LENGTH       = 1
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # log
        log.debug("received data {0}".format(input))
        # parse packet
        try:
           (moteId,
            callingComponent,
            error_code,
            arg1,
            arg2) = struct.unpack('<HBBHH',''.join([chr(c) for c in input]))
         
        except struct.error:
            #print "PARSER ERROR could not extract data from {0}".format(input)
            raise ParserException(ParserException.DESERIALIZE,"could not extract data from {0}".format(input))
        # turn into string
        
        output = "[{COMPONENT}] {ERROR_DESC}".format(
                                    COMPONENT  = self._translateCallingComponent(callingComponent),
                                    ERROR_DESC = self._translateErrorDescription(error_code,arg1,arg2)
                                )
        # log
        log.debug("error = {0}".format(output))
        
        return ('error',input)
    
    #======================== private =========================================
    
    def _translateCallingComponent(self,callingComponent):
        try:
            return StackDefines.components[callingComponent]
        except KeyError:
            return "unknown component code {0}".format(callingComponent)
    
    def _translateErrorDescription(self,error_code,arg1,arg2):
        try:
            return StackDefines.errorDescriptions[error_code].format(arg1,arg2)
        except KeyError:
            return "unknown error {0} arg1={1} arg2={2}".format(error_code,arg1,arg2)