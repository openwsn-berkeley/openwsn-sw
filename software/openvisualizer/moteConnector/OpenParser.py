
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('OpenParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from ParserException import ParserException
import Parser
import ParserStatus
import ParserInfoErrorCritical as ParserIEC
import ParserData

class OpenParser(Parser.Parser):
    
    HEADER_LENGTH  = 1
    
    SERFRAME_MOTE2PC_DATA         = ord('D')
    SERFRAME_MOTE2PC_STATUS       = ord('S')
    SERFRAME_MOTE2PC_INFO         = ParserIEC.ParserInfoErrorCritical.SEVERITY_INFO
    SERFRAME_MOTE2PC_ERROR        = ParserIEC.ParserInfoErrorCritical.SEVERITY_ERROR
    SERFRAME_MOTE2PC_CRITICAL     = ParserIEC.ParserInfoErrorCritical.SEVERITY_CRITICAL
    SERFRAME_MOTE2PC_REQUEST      = ord('R')
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        # subparser objects
        self.parserStatus    = ParserStatus.ParserStatus()
        self.parserInfo      = ParserIEC.ParserInfoErrorCritical(self.SERFRAME_MOTE2PC_INFO)
        self.parserError     = ParserIEC.ParserInfoErrorCritical(self.SERFRAME_MOTE2PC_ERROR)
        self.parserCritical  = ParserIEC.ParserInfoErrorCritical(self.SERFRAME_MOTE2PC_CRITICAL)
        self.parserData      = ParserData.ParserData()
        
        # register subparsers
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_DATA,
            parser = self.parserData.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_STATUS,
            parser = self.parserStatus.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_INFO,
            parser = self.parserInfo.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_ERROR,
            parser = self.parserError.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_CRITICAL,
            parser = self.parserCritical.parseInput,
        )
    
    #======================== public ==========================================
    
    #======================== private =========================================