import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserFactory')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from epparser.specificparsers import *
from ParserException import IncorrectParserException
from ParserException import UnexistingParserException
from ParserException import NoSubclassException

# creates an instance of an specific parser
class ParserFactory(object):
    
    #======================== public ==========================================
    #by reflection get all subclasses of SpecificParser
    def getParser(self,name):
        #p=ScheduleParser.ScheduleParser();
        strname="".join(chr(b) for b in name)
        try:
            sub=SpecificParser.SpecificParser.__subclasses__()
            #sub=Parser.Parser.__subclasses__()
        except NoSubclassException:  
            log.error("there are no parsers defined.")
            raise NoSubclassException()
        for cl in sub:
             try:
               instance = cl() #instantiate the subclass
               instance.create(strname) #check if this is the right one.
               return instance #if this is the desired class return its instance.
             except IncorrectParserException:
               log.debug("not this class..")
               
               #do nothing.. look for next one.
        raise UnexistingParserException() #in case the subclass does no exist throw an error. TODO check how to create an exception
    #======================== private =========================================
