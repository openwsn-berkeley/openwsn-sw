import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SpecificParser')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import struct

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
        # make sure that this function is celled from a subclass
        assert packetStructure
        
        # determine the number of elements
        # Note:  we assume that there is no length byte for non-repeat payloads
        if self.headerStructure['repeat']:
            headerLength     = 1
            numElems         = payload[0]
        else:
            headerLength     = 0
            numElems         = 1
        
        lengthElem = struct.Struct(self.headerStructure['structure'])
        
        # make sure the payload is of the expected size
        if len(payload)!=headerLength+numElems*lengthElem:
            raise IncorrectLengthException()
        
        # skip the header
        payload = payload[headerLength:]
            
        # parse the fields
        fields = []
        for i in range(numElems):
            thisfield = {}
            
            # unpack this element
            temp = struct.unpack(self.headerStructure['structure'],
                                 ''.join([chr(b) for b in payload[:lengthElem]]))
            
            assert(len(temp)==len(self.headerStructure['fieldNames']))
            
            # turn temp into a dictionary of fields
            for (tempelem,fieldName) in zip(temp,self.headerStructure['fieldNames']):
                thisfield[fieldName] = tempelem
            
            # add this field to fields
            fields.append(thisfield)
            
            # skip the element
            payload = payload[lengthElem:]
               
        return fields
    
    #======================== private =========================================
