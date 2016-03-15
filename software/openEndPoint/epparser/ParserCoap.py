import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserCoap')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import Parser
import CoapCodes
import CoapHeader
import Payload
import binascii

# Parses the Coap Header and encodes the payload as an Hex string.
class ParserCoap(Parser.Parser):
    
    #======================== public ==========================================
    
    def parse(self, data):
        returnVal = {}

        log.debug('parsing coap header')
   
        header = self.parseBasicHeader(data)
        
        log.debug('parsing option list')

        option_pointer = self.parseOptionList(data, header)
        
        returnVal['header'] = header
        
        log.debug('reading payload')
        
        payload = Payload.Payload()
        payload.setPayload(data[option_pointer:])
        
        log.debug("Coap msg parsed")
        
        returnVal['payload'] = payload

        #here we can use a factory to get an appropiate parser.or instead use the ParserPayload

        return returnVal
    
    #======================== private =========================================
    def parseBasicHeader(self, data):
        header = CoapHeader.CoapHeader()
        #Header elements
        header.setVersion(int(((data[0]) & 0xc0) >> 6))
        header.setType(int(((data[0]) & 0x30) >> 4))
        header.setOption(int(((data[0]) & 0xF)))
        header.setCode(int((data[1])))
        #for now we only deal with code=3(PUT) code=2(POST)
        header.setMID(int(str(data[2:4]).encode("hex"), 16))
        return header


    def parseOptionList(self, data, header):
        optionList = []
        option_pointer = 4
        for i in range(0, header.getOption()):
            optionDelta = int(((data[option_pointer]) & 0b11110000) >> 4)
            optionNumber = optionDelta
            if i > 0:
                optionNumber = optionDelta + optionList[i - 1][0]
            length = int((data[option_pointer]) & 0b00001111)
            #print data[option_pointer+1:option_pointer+length+1]
            option_payload = data[option_pointer + 1:option_pointer + length + 1]
            option_desc = "" #string describing option
        
            try:
              option_desc = option_codes[optionNumber] #try to get a string to associate with the option code, if none exists use the number
            except:
              pass
            optionList.append([optionDelta, length, option_desc, option_payload])
            option_pointer = option_pointer + length + 1 #pass
        #end for
        header.setOptionList(optionList)
        return option_pointer