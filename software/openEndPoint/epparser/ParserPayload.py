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

# Parses the payload
class ParserPayload(ParserCoap.ParserCoap):
    
    #======================== public ==========================================
    
    def parse(self,data):
        returnVal=super(ParserNeighbors, self).parse(self,data)

        #call the factory for a specific parser
        app=returnVal['header'].optionList[3] ##this is the application name
        factory=ParserFactory.ParserFactory()
        specificParser=factory.getParser(app)#get the specific parser
        returnVal['parsed']=specificParser.parse(returnVal['payload'])#call the parse method
	return returnVal
    
    #======================== private =========================================
