
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
    
    HEADER_LENGTH  = 2
    
    IPHC_SAM       = 4
    IPHC_DAM       = 0
     
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # log
        log.debug("received data {0}".format(input))
        print input
        # ensure input not short longer than header
        self._checkLength(input)
    
        headerBytes = input[:2]
        dest = input[2:10]
        source = input[10:18]
        
        a="".join(hex(c) for c in dest)
        print "dest="+a
        a="".join(hex(c) for c in source)
        print "source="+a
        
        
        iphcHeader  = input[18:20]
        
        # check if local data or internet data. to do so we need to look at the header and see if it is compressed.
        # this is the situation where DAM and SAM fields are 0x03 or 0x02
        
        #from 6LoWPAN compression draft:
        # DAM/SAM 
        # 0 bits.  The address is fully elided.  The first 64 bits
        #    of the address are the link-local prefix padded with zeros.
        #    The remaining 64 bits are computed from the encapsulating
        #    header (e.g. 802.15.4 or IPv6 destination address)
        sam  = (iphcHeader[1] >> self.IPHC_SAM) & 0x03 #2b
        dam  = (iphcHeader[1] >> self.IPHC_DAM) & 0x03 #2b
        
        # for DAO DAM and SAM are 2.
        print "dam and sam are {0},{1}".format(dam,sam) 
        if (dam ==0x03 and sam==0x03): 
            #header byte 1 contains DAM/SAM, if any of both is compressed 
            eventType = 'data.local'
            #keep src and dest for local data 
            input = input[2:]
        else:
            eventType = 'data.internet'
            
            # extract moteId and statusElem
            try:
               (moteId) = struct.unpack('<H',''.join([chr(c) for c in headerBytes]))
            except struct.error:
                raise ParserException(ParserException.DESERIALIZE,"could not extract moteId from {0}".format(headerBytes))
            
            
            # log
            log.debug("moteId={0}".format(moteId))
            #remove src and dest and mote id at the beginning.
            input = input[18:]
             
        # jump the header bytes
       
        
        return (eventType,input)
    
    #======================== private =========================================