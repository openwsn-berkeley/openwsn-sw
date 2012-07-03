
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserData')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from ParserException import ParserException
import Parser

import csv

class ParserData(Parser.Parser):
    
    CSV_FILENAME = 'rawdata.csv'
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # create a csv writer
        self.csvWriter = csv.writer(open(self.CSV_FILENAME, 'wb'), delimiter=',')
        
        # initialize parent class
        Parser.Parser.__init__(self,1)
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        print input
        
        # log
        log.debug("received data {0}".format(input))
        
        # write csv
        self.csvWriter.writerow(input)
        
        raise ParserException(ParserException.NOT_IMPLEMENTED)
    
    #======================== private =========================================