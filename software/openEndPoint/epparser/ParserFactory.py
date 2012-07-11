import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserFactory')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Parser
import CoapCodes
import Payload
import ParserCoap

# creates an instance of an specific parser
class ParserFactory():
    
    #======================== public ==========================================
    #by reflection get all subclasses of SpecificParser
    def getParser(self,name):
        subclasses=SpecificParser.__subclasses__()
        for cl in subclasses:
             try:
               instance = eval(cl)() #instantiate the subclass
               instance.create(name) #check if this is the right one.
               return instance #if this is the desired class return its instance.
             except:
               log.debug("not this class..")
               #do nothing.. look for next one.
        raise Error() #in case the subclass does no exist throw an error. TODO check how to create an exception
    #======================== private =========================================
