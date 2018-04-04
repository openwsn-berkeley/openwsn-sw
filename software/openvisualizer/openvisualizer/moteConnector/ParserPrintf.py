# Copyright (c) 2017, CNRS. 
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
    
    STRING = 0
    INT32 = 1

   
    def __init__(self):
        
        # log
        log.debug('create ParserPrintf instance')
          
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',           # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]
        
        self.buf_addr = ""    #address for the buffer
        self.buf_txt  = ""    #buffer for the messages (to flush when I receive a '\n')
        self.buf_asn = ""
    
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

    #prints the content of the buffer and flushes it
    def flush(self):
             
         print("(asn={0}) from {1}: {2}\n".format(
                self.buf_asn,
                self.buf_addr,
                self.buf_txt
                )
             )
         
         log.info("(asn={0}) from {1}: {2}\n".format(
                self.buf_asn,
                self.buf_addr,
                self.buf_txt
                )
             )
          
         self.buf_txt = ""
         self.buf_addr = ""
         self.buf_asn = ""
         
    def parseInput(self,input):
      
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('received printf {0}'.format(input))
         
        #subtype: string
        if (input[0] == self.STRING) :
            self.buf_addr = self.BytesToAddr(input[1:3])
            self.buf_asn  = self.BytesToString(input[3:8])
            for c in input[8:] :
                if (c == 10):   #EOL
                    self.flush()
                self.buf_txt = self.buf_txt + unichr(c)
        
            #subtype integer
        elif(input[0] == self.INT32):
            self.buf_txt = self.buf_txt + self.BytesToString(input[1:5])
        else:
            print("Unkwnon printf subtype\n")
        
        #everything was fine  
        return ('error', input)


    def _translateCallingComponent(self,callingComponent):
        try:
            return StackDefines.components[callingComponent]
        except KeyError:
            return "unknown component code {0}".format(callingComponent)

 #======================== private =========================================
 
  
