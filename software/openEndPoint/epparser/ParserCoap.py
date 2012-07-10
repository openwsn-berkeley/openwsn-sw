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
    
    def parse(self,data):
        returnVal          = {}
        
       
	log.debug('parsing coap header')
   
        header = CoapHeader.CoapHeader()
#vader.vader -- I have doubts here. Should I use ord?? Look commented code versus non commented (the difference is ord)

        #Header elements
#        header.setVersion(int((ord(data[0])& 0xc0) >> 6))
#        header.setType(int((ord(data[0])& 0x30) >> 4))
#        header.setOption(int((ord(data[0])& 0xF)))
#        header.setCode (int(ord(data[1])))

        header.setVersion(int(((data[0])& 0xc0) >> 6))
        header.setType(int(((data[0])& 0x30) >> 4))
        header.setOption(int(((data[0])& 0xF)))
        header.setCode (int((data[1])))
       
        #for now we only deal with code=3(PUT) code=2(POST)
        header.setMID(int(str(data[2:4]).encode("hex"),16))
        
        log.debug('parsing option list')

        optionList = []
        option_pointer = 4
        #print version,type,options,code
	for i in range(0, header.getOption()):
            #optionDelta = int((ord(data[option_pointer])&0b11110000)>>4)
            optionDelta = int(((data[option_pointer])&0b11110000)>>4)
            optionNumber = optionDelta
            if (i > 0):
               optionNumber = optionDelta + optionList[i-1][0]
#vader.vader -- idem as previous comment regarding ord.
            #length = int(ord(data[option_pointer])&0b00001111)
            length = int((data[option_pointer])&0b00001111)
            print data[option_pointer+1:option_pointer+length+1]
	    option_payload = data[option_pointer+1:option_pointer+length+1]
            option_desc = "" #string describing option
	    try:
                #try to get a string to associate with the option code, if none exists use the number
                option_desc = option_codes[optionNumber]
	    except:
               pass
            optionList.append([optionDelta, length, option_desc, option_payload])
            option_pointer = option_pointer + length + 1
        
        header.setOptionList(optionList)
        
        returnVal['header'] = header

        log.debug('reading payload')
        payload = Payload.Payload()
        #vader.vader -- how to get the payload? If I use hexlify it throws an error.
        #payload.setPayload(str(binascii.hexlify(data[option_pointer:])))
        payload.setPayload("aaaaa")
        log.debug("Coap msg parsed")
	returnVal['payload'] = payload

        return returnVal
    
    #======================== private =========================================
