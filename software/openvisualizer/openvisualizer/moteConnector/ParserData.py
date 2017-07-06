# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('ParserData')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import struct

from pydispatch import dispatcher

from ParserException import ParserException
import Parser

class ParserData(Parser.Parser):
    
    HEADER_LENGTH  = 2
    MSPERSLOT      = 15 #ms per slot.
    
    IPHC_SAM       = 4
    IPHC_DAM       = 0
    
    UINJECT_MASK    = 'uinject'
     
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',                     # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]
    
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        # log
        if log.isEnabledFor(logging.DEBUG):
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
        
        if log.isEnabledFor(logging.DEBUG):
            a="".join(hex(c) for c in dest)
            log.debug("destination address of the packet is {0} ".format(a))
        
        if log.isEnabledFor(logging.DEBUG):
            a="".join(hex(c) for c in source)
            log.debug("source address (just previous hop) of the packet is {0} ".format(a))
        
        # remove asn src and dest and mote id at the beginning.
        # this is a hack for latency measurements... TODO, move latency to an app listening on the corresponding port.
        # inject end_asn into the packet as well
        input = input[23:]
        
        if log.isEnabledFor(logging.DEBUG):
            log.debug("packet without source,dest and asn {0}".format(input))
        
        # when the packet goes to internet it comes with the asn at the beginning as timestamp.
         
        # cross layer trick here. capture UDP packet from udpLatency and get ASN to compute latency.
        if len(input) >37:
            if self.UINJECT_MASK == ''.join(chr(i) for i in input[-7:]):
                aux      = input[len(input)-14:len(input)-9]  # last 5 bytes of the packet are the ASN in the UDP latency packet
                diff     = self._asndiference(aux,asnbytes)   # calculate difference 
                timeinus = diff*self.MSPERSLOT                # compute time in ms
                SN       = input[len(input)-9:len(input)-7]   # SN sent by mote
                if timeinus<0xFFFF:
                    # print "source {0}, dest {1}, timeinus {2}ms, SN {3}".format(source, dest,timeinus,SN)
                    pass
                else:
                    # this usually happens when the serial port framing is not correct and more than one message is parsed at the same time. this will be solved with HDLC framing.
                    print "Wrong latency computation {0} = {1} mS".format(str(node),timeinus)
                    print ",".join(hex(c) for c in input)
                    log.warning("Wrong latency computation {0} = {1} mS".format(str(node),timeinus))
                    pass
                # in case we want to send the computed time to internet..
                # computed=struct.pack('<H', timeinus)#to be appended to the pkt
                # for x in computed:
                    #input.append(x)
            else:
                # no udplatency
                # print input
                pass     
        else:
            pass      
       
        eventType='data'
        # notify a tuple including source as one hop away nodes elide SRC address as can be inferred from MAC layer header
        return eventType, (source, input)

 #======================== private =========================================
 
    def _asndiference(self,init,end):
      
       asninit = struct.unpack('<HHB',''.join([chr(c) for c in init]))
       asnend  = struct.unpack('<HHB',''.join([chr(c) for c in end]))
       if asnend[2] != asninit[2]: #'byte4'
          return 0xFFFFFFFF
       else:
           pass
       
       diff = 0
       if asnend[1] == asninit[1]:#'bytes2and3'
          return asnend[0]-asninit[0]#'bytes0and1'
       else:
          if asnend[1]-asninit[1]==1:##'bytes2and3'              diff  = asnend[0]#'bytes0and1'
              diff += 0xffff-asninit[0]#'bytes0and1'
              diff += 1
          else:   
              diff = 0xFFFFFFFF
       
       return diff