import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserPayload')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Parser
import CoapCodes
import Payload
import ParserCoap

PATH_FIELD = 3

# Parses the payload
class ParserPayload(ParserCoap.ParserCoap):
    
    #======================== public ==========================================
    
    def parse(self,data):
        returnVal=ParserCoap.ParserCoap.parse(self,data)
        #super(ParserPayload, self).parse(self,data)

        #call the factory for a specific parser
        app=returnVal['header'].optionList[PATH_FIELD] ##this is the application name
        factory=ParserFactory.ParserFactory()
       
        try:
            specificParser=factory.getParser(app)#get the specific parser
        except UnexistingParserException:
            raise UnexistingParserException('Parser for that payload does not exists')
        #TODO.. how to return here??
        returnVal['parsed']=specificParser.parse(returnVal['payload'])#call the parse method
	return returnVal
    
    #======================== private =========================================
