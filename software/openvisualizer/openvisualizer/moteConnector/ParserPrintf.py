# Copyright (c) 2015, CNRS. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging
log = logging.getLogger('ParserPrintf')
log.setLevel(logging.INFO)
log.addHandler(logging.NullHandler())

import struct

from pydispatch import dispatcher
import StackDefines

from ParserException import ParserException
import Parser

class ParserPrintf(Parser.Parser):
    
    HEADER_LENGTH  = 2
    MSPERSLOT      = 15 #ms per slot.
   
    def __init__(self):
        
        # log
        log.debug('create ParserPrintf instance')
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',           # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]
    
    #returns a string with the decimal value of a uint16_t
    def BytesToString(self, bytes):
        str = ''
        i = 0

        #print bytes

        for byte in bytes:
            str = format(eval('{0} + {1} * 256 ** {2}'.format(str, byte, i)))
            #print ('{0}:{1}'.format(i, str)) 
            i = i + 1      

        return(str)

    def BytesToStr(self, bytes):
        str = ''
        i = 0

        for byte in bytes:
            str = str + unichr(byte) 


        return(str)

    def BytesToAddr(self, bytes):
        str = ''
        i = 0

        for byte in bytes:
            str = str + '{:02x}'.format(byte) 
            #if (i < len(bytes)-1):
            #    str = str + '-'
            i += 1

        return(str)


    def parseInput(self,input):
      
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('received printf {0}'.format(input))
         
         
        #headers
        addr = input[:2]  
        COMPONENT  = self._translateCallingComponent(input[2])
        asnbytes = input[3:8]
        (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes]))
        msg = input[8:]

        print("(asn={2}) from {0}:{1}:{3}".format(
                self.BytesToAddr(addr),
                COMPONENT,
                self.BytesToString(asnbytes),
                self.BytesToStr(msg)
                ))
        
        log.info("(asn={2}) from {0}:{1}:{3}".format(
                self.BytesToAddr(addr),
                COMPONENT,
                self.BytesToString(asnbytes),
                self.BytesToStr(msg)
                ))
       
        return ('error', input)

    def _translateCallingComponent(self,callingComponent):
        try:
            return StackDefines.components[callingComponent]
        except KeyError:
            return "unknown component code {0}".format(callingComponent)

 #======================== private =========================================
 
  
