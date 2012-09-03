
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
    
    TYPE_DATA_LOCAL      = ord('L')
    TYPE_DATA_INTERNET   = ord('I')
    
    
    IPHC_SAM              = 4
    IPHC_DAM              = 0
    
     
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
    
    #======================== public ==========================================
    
    def parseInput(self,key_param,input):
        
        # log
        log.debug("received data {0}".format(input))
        #print " ".join(hex(i) for i in input)
        #print input
        # ensure input not short longer than header
        self._checkLength(input)
        
    
        #headerBytes = input[:2]
        headerBytes = input[:2]
        iphcHeader = input[2:4]
        # check if local data or internet data. to do so we need to look at the header and see if it is compressed.
        # this is the situation where DAM and SAM fields are 0x03 or 0x02
        
        #from 6lowpan compression draft:
        #DAM/SAM 
        #0 bits.  The address is fully elided.  The first 64 bits
        #    of the address are the link-local prefix padded with zeros.
        #    The remaining 64 bits are computed from the encapsulating
        #    header (e.g. 802.15.4 or IPv6 destination address)
        sam  = (iphcHeader[1] >> self.IPHC_SAM) & 0x03 #2b
        dam  = (iphcHeader[1] >> self.IPHC_DAM) & 0x03 #2b
        
        #for DAO DAM and SAM are 2.
         
        if (dam ==0x02 and sam==0x02): 
            #header byte 1 contains DAM/SAM, if any of both is compressed 
            key_param=self.TYPE_DATA_LOCAL #this is a link local messagage, we need to parse it and then return 
            
            #parse here the DAO.  
            #do nothing and return 
        else:
            key_param=self.TYPE_DATA_INTERNET     
            #debug ..
            #key=self.TYPE_DATA_LOCAL #this is a link local messagage, we need to parse it and then return 
            
            # extract moteId and statusElem
            try:
               (moteId) = struct.unpack('<H',''.join([chr(c) for c in headerBytes]))
            except struct.error:
                raise ParserException(ParserException.DESERIALIZE,"could not extract moteId from {0}".format(headerBytes))
            # log
            log.debug("moteId={0}".format(moteId))
        
        # jump the header bytes
        input = input[2:]
        
        return (key_param,input)
    
    #======================== private =========================================