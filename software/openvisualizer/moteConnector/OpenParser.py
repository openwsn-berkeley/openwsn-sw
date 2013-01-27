
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
    
    TYPE_DATA            = ord('D')
    TYPE_STATUS          = ord('S')
    TYPE_INFO            = ParserIEC.ParserInfoErrorCritical.SEVERITY_INFO
    TYPE_ERROR           = ParserIEC.ParserInfoErrorCritical.SEVERITY_ERROR
    TYPE_CRITICAL        = ParserIEC.ParserInfoErrorCritical.SEVERITY_CRITICAL
    TYPE_ALL             = [TYPE_DATA,
                            TYPE_STATUS,
                            TYPE_INFO,
                            TYPE_ERROR,
                            TYPE_CRITICAL,]
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        # subparser objects
        self.parserStatus    = ParserStatus.ParserStatus()
        self.parserInfo      = ParserIEC.ParserInfoErrorCritical(self.TYPE_INFO)
        self.parserError     = ParserIEC.ParserInfoErrorCritical(self.TYPE_ERROR)
        self.parserCritical  = ParserIEC.ParserInfoErrorCritical(self.TYPE_CRITICAL)
        self.parserData      = ParserData.ParserData()
        
        # register subparsers
        self._addSubParser(index=0,  val=self.TYPE_STATUS,     parser=self.parserStatus.parseInput)
        self._addSubParser(index=0,  val=self.TYPE_INFO,       parser=self.parserInfo.parseInput)
        self._addSubParser(index=0,  val=self.TYPE_ERROR,      parser=self.parserError.parseInput)
        self._addSubParser(index=0,  val=self.TYPE_CRITICAL,   parser=self.parserCritical.parseInput)
        self._addSubParser(index=0,  val=self.TYPE_DATA,       parser=self.parserData.parseInput)
    
    #======================== public ==========================================
    
    #======================== private =========================================