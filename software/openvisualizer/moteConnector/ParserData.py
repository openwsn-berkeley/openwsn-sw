
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserData')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import struct

from pydispatch import dispatcher

from ParserException import ParserException
import Parser

class ParserData(Parser.Parser):
    
    HEADER_LENGTH  = 2
    uSPERTIC       = 33 #uS per tic.
    
    IPHC_SAM       = 4
    IPHC_DAM       = 0
    
     
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',                     # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]
    
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # log
        log.debug("received data {0}".format(input))
    
        # ensure input not short longer than header
        self._checkLength(input)
    
        headerBytes = input[:2]
        
        asnbytes=input[2:7]
        (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes]))
        
        
        dest = input[7:15]
        source = input[15:23]
        
        a="".join(hex(c) for c in dest)
        log.debug("destination address of the packet is {0} ".format(a))
        a="".join(hex(c) for c in source)
        log.debug("source address of the packet is {0} ".format(a))
       
       
        if (len(input) > 25):
            iphcHeader  = input[13:25]
            
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
                icmpHeader = input[25:27]
                source=input[27:35]
                rplheader=input[35:37]
    
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
            #remove asn src and dest and mote id at the beginning.
        input = input[23:]
        #when the packet goes to internet it comes with the asn at the beginning as timestamp.
        
        #cross layer trick here. capture UDP packet from udpLatency and get ASN to compute latency.
        #then notify a latency component that will plot that information.
        
        #[237, 0, 48, 4, 0, 0, 0, 120, 0, 17, 64, 0, 0, 0, 0, 0, 0, 0, 0, 20, 21, 146, 11, 3, 1, 0, 230, 32, 1, 4, 112, 0, 102, 0, 23, 0, 0, 
        # 0, 0, 0, 0, 0, 2, 238, 73, 238, 73, 0, 21, 124, 45, 20, 21, 146, 11, 3, 1, 0, 230, 46, 4, 0, 0, 0]
             
        #0x58,0x3,0x0,0x0,0x0,0x3,0x1,0x0,0xe6,0x20,0x1,0x4,0x70,0x0,0x66,0x0,0x17,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x2,0xee,0x49,0xee,0x49,0x0,0x15,0x55,0x2e,0x14,0x15,0x92,0xb,0x3,0x1,0x0,0xe6,0x55,0x3,0x0,0x0,0x0
        # port 61001==0xee,0x49
        if (len(input) > 23):
           if (input[22]==238 and input[23]==73):
            #udp port 61001 for udplatency app.
               aux=input[len(input)-5:]
               diff=self._asndiference(aux,asnbytes)
               timeinus=diff*self.uSPERTIC
               node=input[len(input)-13:len(input)-5]
               #print "Node {0} = {1} uS".format(hex(node[7]),timeinus)
               #log.debug("Node {0} = {1} uS".format(hex(node[7]),timeinus))
               
               if (timeinus<0xFFFF):
               #notify latency manager component. only if a valid value
                  dispatcher.send(
                     signal        = 'latency',
                     sender        = 'parserData',
                     data          = (node,timeinus),
                  )
               else:
                   print "Wrong latency computation {0} = {1} uS".format(str(node),timeinus)
                   log.debug("Wrong latency computation {0} = {1} uS".format(str(node),timeinus))
                   pass
               #computed=struct.pack('<H', timeinus)#to be appended to the pkt
               #for x in computed:
                   #input.append(x)
           else:
               pass     
        else:
           pass      
        return (eventType,input)

 #======================== private =========================================
 
    def _asndiference(self,init,end):
      
       asninit = struct.unpack('<HHB',''.join([chr(c) for c in init]))
       asnend  = struct.unpack('<HHB',''.join([chr(c) for c in end]))
       if (asnend[2] != asninit[2]): #'byte4'
          return 0xFFFFFFFF
       else:
           pass
       
       diff = 0;
       if (asnend[1] == asninit[1]):#'bytes2and3'
          return asnend[0]-asninit[0]#'bytes0and1'
       else:
          if (asnend[1]-asninit[1]==1):##'bytes2and3'              diff  = asnend[0]#'bytes0and1'
              diff += 0xffff-asninit[0]#'bytes0and1'
              diff += 1;
          else:   
              diff = 0xFFFFFFFF
       
       return diff