
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
    MSPERSLOT       = 15 #ms per slot.
    
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
        #asn comes in the next 5bytes.  
        asnbytes=input[2:7]
        (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes]))
        
        #source and destination of the message
        dest = input[7:15]
        #source is elided!!! so it is not there.. check that.
        source = input[15:23]
        
        a="".join(hex(c) for c in dest)
        log.debug("destination address of the packet is {0} ".format(a))
        #print a
        a="".join(hex(c) for c in source)
        log.debug("source address (just previous hop) of the packet is {0} ".format(a))
        
        
        #check if the message is local or internet
        if (len(input) > 35):
            iphcHeader  = input[23:35]
            #from 6LoWPAN compression draft:
            # DAM/SAM 
            # 0 bits.  The address is fully elided.  The first 64 bits
            #    of the address are the link-local prefix padded with zeros.
            #    The remaining 64 bits are computed from the encapsulating
            #    header (e.g. 802.15.4 or IPv6 destination address) 
            sam  = (iphcHeader[1] >> self.IPHC_SAM) & 0x03 #2b
            dam  = (iphcHeader[1] >> self.IPHC_DAM) & 0x03 #2b
            
            if (dam==0x03):
                if (sam==0x03):
                    #first hop only
                    log.debug("local pkt from first hop as src address is elided")
                    #rplheader=input[27:29]
                    #inject source address to the packet so the DAO parsing is the same in any case.
                    src=[]
                    src=list(source)
                    dao=[]
                    dao=list(input[:27])
                    dao.extend(src)
                    dao.extend(list(input[27:]))
                    input=list(dao)
                    rplheader=input[35:37]
                        
                elif (sam==0x01):
                    #rest of hops src is not compressed 
                    log.debug("local pkt from further hop as src address is not elided")
                    source=input[27:35]
                    for i in range(len(source)):
                        input[15+i]=input[27+i]
                        
                    a="".join(hex(c) for c in source)
                    log.debug("source address of the packet is {0} ".format(a))
                    #print a
                    
                    rplheader=input[35:37]  
                else:
                    log.error("local pkt with src address in 128b format.. this should never happen.")
                    while 1:
                        pass
                            
                #source is not elided so it is in the iphc header.
                #skip 2 bytes of ICMP header being nexhop, hop limit,..
                icmpHeader = input[25:27]
    
                if (rplheader[0]==155 and rplheader[1]==4):
                    #this is a DAO
                    eventType = 'data.local'
                    #keep src and dest for local data --remove asn though
                    input = input[7:]
                    log.debug("data is local")  
                    
                    return (eventType,input)
                else:
                    pass
            else:
                pass
        else:
            pass
        
        #No DAO, it is data Internet.
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
        #print input      
        #when the packet goes to internet it comes with the asn at the beginning as timestamp.
        #TODO encapsulate this into a function.. 
        #cross layer trick here. capture UDP packet from udpLatency and get ASN to compute latency.
        #then notify a latency component that will plot that information.
        # port 61001==0xee,0x49
        if (len(input) >37):
           if (input[36]==238 and input[37]==73):
            #udp port 61001 for udplatency app.
               aux=input[len(input)-5:]                 #last 5 bytes of the packet are the ASN in the UDP latency packet
               diff=self._asndiference(aux,asnbytes)    #calculate difference 
               timeinus=diff*self.MSPERSLOT             #compute time in ms 
               parent=input[len(input)-21:len(input)-13]#the parent node is the first element (used to know topology)
               node=input[len(input)-13:len(input)-5] #the node address
               
               if (timeinus<0xFFFF):
               #notify latency manager component. only if a valid value
                  dispatcher.send(
                     signal        = 'latency',
                     sender        = 'parserData',
                     data          = (node,timeinus,parent),
                  )
               else:
                   #this usually happens when the serial port framing is not correct and more than one message is parsed at the same time. this will be solved with HDLC framing.
                   print "Wrong latency computation {0} = {1} mS".format(str(node),timeinus)
                   print ",".join(hex(c) for c in input)
                   log.debug("Wrong latency computation {0} = {1} mS".format(str(node),timeinus))
                   pass
               #in case we want to send the computed time to internet..
               #computed=struct.pack('<H', timeinus)#to be appended to the pkt
               #for x in computed:
                   #input.append(x)
           else:
               #no udplatency
               #print input
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