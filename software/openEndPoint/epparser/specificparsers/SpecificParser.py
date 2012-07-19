import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SpecificParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import struct
from ..ParserException import IncorrectParserException,IncorrectLengthException

#interface implemented by specific parsers. Implement that interface if you want to parse an specific payload.
class SpecificParser(object):

    headerStructure = {}
    
    #======================== public ==========================================
    
    #returns if name matches to the name defined in the implementing class. If not throws an exception.
    def create(self, name):
        raise NotImplemeterError()

    def parse(self,payload):
        '''
        \brief Generic parser.
        '''
        # make sure that this function is called from a subclass
        assert self.headerStructure
        
        # determine the number of elements
        # Note:  we assume that there is no length byte for non-repeat payloads
        if self.headerStructure['repeat']:
            headerLength     = 1
            numElems         = payload.getPayload()[0]
        else:
            headerLength     = 0
            numElems         = 1
       
        st=self.headerStructure['structure']
        lengthElem = struct.calcsize(st)
        
        # make sure the payload is of the expected size
        lo=len(payload.getPayload())
        if lo!=headerLength+numElems*lengthElem:
            raise IncorrectLengthException()
        
        # skip the header
        pay = payload.getPayload()[headerLength:]
            
        # parse the fields
        fields = []
        for i in range(numElems):
            thisfield = {}
            
            # unpack this element
            aux=''.join([chr(b) for b in pay[:lengthElem]])
            temp = struct.unpack(self.headerStructure['structure'],aux)
            
            assert(len(temp)==len(self.headerStructure['fieldNames']))
            
            # turn temp into a dictionary of fields
            for (tempelem,fieldName) in zip(temp,self.headerStructure['fieldNames']):
                thisfield[fieldName] = tempelem
            
            # add this field to fields
            fields.append(thisfield)
            
            # skip the element
            pay = pay[lengthElem:]
        
        log.debug("parsed payload {} ".format(fields))       
        return fields
    
    #======================== private =========================================
