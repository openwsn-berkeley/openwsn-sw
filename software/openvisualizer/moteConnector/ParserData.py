
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
    
        # ensure input not short longer than header
        self._checkLength(input)
    
        headerBytes = input[:2]
        dest = input[2:10]
        source = input[10:18]
        
        a="".join(hex(c) for c in dest)
        log.debug("destination address of the packet is {0} ".format(a))
        a="".join(hex(c) for c in source)
        log.debug("source address of the packet is {0} ".format(a))
       
       
        if (len(input) > 20):
            iphcHeader  = input[18:20]
            
            #from 6LoWPAN compression draft:
            # DAM/SAM 
            # 0 bits.  The address is fully elided.  The first 64 bits
            #    of the address are the link-local prefix padded with zeros.
            #    The remaining 64 bits are computed from the encapsulating
            #    header (e.g. 802.15.4 or IPv6 destination address)
            
            sam  = (iphcHeader[1] >> self.IPHC_SAM) & 0x03 #2b
            dam  = (iphcHeader[1] >> self.IPHC_DAM) & 0x03 #2b
            
            if (sam==0x01 and dam==0x03):
                #source is not elided so it is in the iphc header.
                #skip 2 bytes of ICMP header being nexhop, hop limit,..
                icmpHeader = input[20:22]
                source=input[22:30]
                rplheader=input[30:32]
    
                if (rplheader[0]==155 and rplheader[1]==4):
                    #this is a DAO
                    eventType = 'data.local'
                    #keep src and dest for local data 
                    input = input[2:]
                    log.debug("data is local")  
                    
                    return (eventType,input)
                else:
                    pass
            else:
                pass
        else:
            pass
        
        #No DAO, it is data internet.
        eventType = 'data.internet'
        log.debug("data destination is in internet")
            # extract moteId and statusElem
        try:
          (moteId) = struct.unpack('<H',''.join([chr(c) for c in headerBytes]))
        except struct.error:
           raise ParserException(ParserException.DESERIALIZE,"could not extract moteId from {0}".format(headerBytes))
            
            
            # log
        log.debug("moteId={0}".format(moteId))
            #remove src and dest and mote id at the beginning.
        input = input[18:]
             
        return (eventType,input)
    
    #======================== private =========================================