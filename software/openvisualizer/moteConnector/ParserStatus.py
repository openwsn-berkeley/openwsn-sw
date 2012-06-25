import collections
import struct

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ParserStatus')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from ParserException import ParserException
import Parser

class FieldParsingKey(object):

    def __init__(self,index,val,structure,tuple):
        self.index      = index
        self.val        = val
        self.structure  = structure
        self.tuple      = tuple

class ParserStatus(Parser.Parser):
    
    HEADER_LENGTH       = 4
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        # local variables
        self.fieldsParsingKeys    = []
        
        # register fields
        self._addFieldsParser   (
                                    3,
                                    0,
                                    '<B',
                                    collections.namedtuple(
                                        'tuple_status_isSync',
                                        [
                                            'isSync',                          # B
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    1,
                                    '<BBxHQHQ',
                                    collections.namedtuple(
                                        'tuple_status_idManager',
                                        [
                                            'isDAGroot',                       # B
                                            'isBridge',                        # B
                                                                               # x
                                            'my16bID',                         # H
                                            'my64bID',                         # Q
                                            'myPANID',                         # H
                                            'myPrefix',                        # Q
                                        ]
                                    )
                                )
        self._addFieldsParser   (   
                                    3,
                                    2,
                                    '<B',
                                    collections.namedtuple(
                                        'tuple_status_myDagRank',
                                        [
                                            'myDAGrank',                       # B
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    3,
                                    '<HH',
                                    collections.namedtuple(
                                        'tuple_status_outputBuffer',
                                        [
                                            'index_write',                     # H
                                            'index_read',                      # H
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    4,
                                    '<H',
                                    collections.namedtuple(
                                        'tuple_status_asn',
                                        [
                                            'asn',                             # H
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    5,
                                    '<BxhhB',
                                    collections.namedtuple(
                                        'tuple_status_macStats',
                                        [
                                            'syncCounter',                     # B
                                                                               # x
                                            'minCorrection',                   # h
                                            'maxCorrection',                   # h
                                            'numDeSync'                        # B
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    6,
                                    '>xBBBBBBQxxxxxxxxBBB',
                                    collections.namedtuple(
                                        'tuple_status_scheduleRow',
                                        [
                                                                               # x
                                            'type',                            # B
                                            'shared',                          # B
                                            'backoffExponent',                 # B
                                            'backoff',                         # B
                                            'channelOffset',                   # B
                                            'addrType',                        # B
                                            'neighbor',                        # Q
                                                                               # xxxxxxx
                                            'numRx',                           # B
                                            'numTx',                           # B
                                            'numTxACK'                         # B
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    7,
                                    '<BB',
                                    collections.namedtuple(
                                        'tuple_status_queueRow',
                                        [
                                            'creator',                         # B
                                            'owner',                           # B
                                        ]
                                    )
                                )
        self._addFieldsParser   (
                                    3,
                                    8,
                                    '>BBBBxQxxxxxxxxBbBBB',
                                    collections.namedtuple(
                                        'tuple_status_neighborsRow',
                                        [
                                            'rowNumber',                       # H
                                            'used',                            # B
                                            'parentPreference',                # B
                                            'stableNeighbor',                  # B
                                            'switchStabilityCounter',          # B
                                                                               # x
                                            'addr_64b',                        # Q
                                                                               # xxxxxxx
                                            'DAGrank',                         # B
                                            'rssi',                            # b
                                            'numRx',                           # B
                                            'numTx',                           # B
                                            'numTxACK',                        # B
                                        ]
                                    )
                                )
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # ensure input not short longer than header
        self._checkLength(input)
        
        # parse the header
        # TODO
        
        # call the next header parser
        for key in self.fieldsParsingKeys:
            if input[key.index]==key.val:
                fields = struct.unpack(key.structure,''.join([chr(c) for c in input]))
                return key.tuple(*fields)
        
        # if you get here, no key was found
        raise ParserException(ParserException.NO_KEY, "type={0} (\"{1}\")".format(
            input[0],
            chr(input[0])))
    
    #======================== private =========================================
    
    def _addFieldsParser(self,index=None,val=None,structure=None,tuple=None):
        self.fieldsParsingKeys.append(FieldParsingKey(index,val,structure,tuple))