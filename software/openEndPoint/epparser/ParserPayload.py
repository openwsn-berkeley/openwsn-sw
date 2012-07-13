import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserPayload')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Parser
import Payload
import ParserCoap
import ParserException

from specificparsers import *

from ParserException import UnexistingParserException
from ParserException import NoSubclassException
from ParserException import IncorrectParserException

import ParserFactory

PATH_FIELD = 1
PATH_SUBFIELD = 3

# Parses the payload
class ParserPayload(ParserCoap.ParserCoap):
    
    #======================== public ==========================================
    
    def parse(self,data):
        returnVal=ParserCoap.ParserCoap.parse(self,data)
        #super(ParserPayload, self).parse(self,data)

        #call the factory for a specific parser
        optionList=returnVal['header'].getOptionList()
        app=optionList[PATH_FIELD] ##this is the application name
        factory=ParserFactory.ParserFactory()
       
        try:
            specificParser=factory.getParser(app[PATH_SUBFIELD])#get the specific parser
        except UnexistingParserException:
            raise UnexistingParserException('Parser for that payload does not exists')
        #TODO.. how to return here??
        returnVal['parsed']=specificParser.parse(returnVal['payload'])#call the parse method
	return returnVal
    
    #======================== private =========================================
