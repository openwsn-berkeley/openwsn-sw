# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('ParserStatus')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import collections
import struct

from ParserException import ParserException
import Parser
import openvisualizer.openvisualizer_utils as u

class FieldParsingKey(object):

    def __init__(self,index,val,name,structure,fields):
        self.index      = index
        self.val        = val
        self.name       = name
        self.structure  = structure
        self.fields     = fields

class ParserStatus(Parser.Parser):
    
    HEADER_LENGTH       = 4
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        # local variables
        self.fieldsParsingKeys    = []
        
        # register fields
        self._addFieldsParser   (
                                    3,
                                    0,
                                    'IsSync',
                                    '<B',
                                    [
                                        'isSync',                    # B
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    1,
                                    'IdManager',
                                    '<BBBBBBBBBBBBBBBBBBBBB',
                                    [
                                        'isDAGroot',                 # B
                                        'myPANID_0',                 # B
                                        'myPANID_1',                 # B
                                        'my16bID_0',                 # B
                                        'my16bID_1',                 # B
                                        'my64bID_0',                 # B
                                        'my64bID_1',                 # B
                                        'my64bID_2',                 # B
                                        'my64bID_3',                 # B
                                        'my64bID_4',                 # B
                                        'my64bID_5',                 # B
                                        'my64bID_6',                 # B
                                        'my64bID_7',                 # B
                                        'myPrefix_0',                # B
                                        'myPrefix_1',                # B
                                        'myPrefix_2',                # B
                                        'myPrefix_3',                # B
                                        'myPrefix_4',                # B
                                        'myPrefix_5',                # B
                                        'myPrefix_6',                # B
                                        'myPrefix_7',                # B
                                    ],
                                )
        self._addFieldsParser   (   
                                    3,
                                    2,
                                    'MyDagRank',
                                    '<H',
                                    [
                                        'myDAGrank',                 # H
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    3,
                                    'OutputBuffer',
                                    '<HH',
                                    [
                                        'index_write',               # H
                                        'index_read',                # H
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    4,
                                    'Asn',
                                    '<BHH',
                                    [
                                        'asn_4',                     # B
                                        'asn_2_3',                   # H
                                        'asn_0_1',                   # H
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    5,
                                    'MacStats',
                                    '<BBhhBII',
                                    [
                                        'numSyncPkt' ,               # B
                                        'numSyncAck',                # B
                                        'minCorrection',             # h
                                        'maxCorrection',             # h
                                        'numDeSync',                 # B
                                        'numTicsOn',                 # I
                                        'numTicsTotal',              # I
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    6,
                                    'ScheduleRow',
                                    '<BHBBBBQQBBBBHH',
                                    [
                                        'row',                       # B
                                        'slotOffset',                # H 
                                        'type',                      # B
                                        'shared',                    # B
                                        'channelOffset',             # B
                                        'neighbor_type',             # B
                                        'neighbor_bodyH',            # Q
                                        'neighbor_bodyL',            # Q
                                        'numRx',                     # B
                                        'numTx',                     # B
                                        'numTxACK',                  # B
                                        'lastUsedAsn_4',             # B
                                        'lastUsedAsn_2_3',           # H
                                        'lastUsedAsn_0_1',           # H
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    7,
                                    'Backoff',
                                    '<BB',
                                    [
                                        'backoffExponent',           # B
                                        'backoff',                   # B
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    8,
                                    'QueueRow',
                                    '<BBBBBBBBBBBBBBBBBBBB',
                                    [
                                        'creator_0',                 # B
                                        'owner_0',                   # B
                                        'creator_1',                 # B
                                        'owner_1',                   # B
                                        'creator_2',                 # B
                                        'owner_2',                   # B
                                        'creator_3',                 # B
                                        'owner_3',                   # B
                                        'creator_4',                 # B
                                        'owner_4',                   # B
                                        'creator_5',                 # B
                                        'owner_5',                   # B
                                        'creator_6',                 # B
                                        'owner_6',                   # B
                                        'creator_7',                 # B
                                        'owner_7',                   # B
                                        'creator_8',                 # B
                                        'owner_8',                   # B
                                        'creator_9',                 # B
                                        'owner_9',                   # B
                                    ],
                                )
        self._addFieldsParser   (
                                    3,
                                    9,
                                    'NeighborsRow',
                                    '<BBBBBBQQHbBBBBBHHB',
                                    [
                                        'row',                       # B
                                        'used',                      # B
                                        'parentPreference',          # B
                                        'stableNeighbor',            # B
                                        'switchStabilityCounter',    # B
                                        'addr_type',                 # B
                                        'addr_bodyH',                # Q
                                        'addr_bodyL',                # Q
                                        'DAGrank',                   # H
                                        'rssi',                      # b
                                        'numRx',                     # B
                                        'numTx',                     # B
                                        'numTxACK',                  # B
                                        'numWraps',                  # B
                                        'asn_4',                     # B
                                        'asn_2_3',                   # H
                                        'asn_0_1',                   # H
                                        'joinPrio',                  # B
                                    ],
                                )
        self._addFieldsParser   (   
                                    3,
                                    10,
                                    'kaPeriod',
                                    '<H',
                                    [
                                        'kaPeriod',                  # H
                                    ],
                                )
    
    #======================== public ==========================================
    
    def parseInput(self,input):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("received input={0}".format(input))
        
        # ensure input not short longer than header
        self._checkLength(input)
        
        headerBytes = input[:3]
        
        # extract moteId and statusElem
        try:
           (moteId,statusElem) = struct.unpack('<HB',''.join([chr(c) for c in headerBytes]))
        except struct.error:
            raise ParserException(ParserException.DESERIALIZE,"could not extract moteId and statusElem from {0}".format(headerBytes))
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("moteId={0} statusElem={1}".format(moteId,statusElem))
        
        # jump the header bytes
        input = input[3:]
        
        # call the next header parser
        for key in self.fieldsParsingKeys:
            if statusElem==key.val:
            
                # log
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("parsing {0}, ({1} bytes) as {2}".format(input,len(input),key.name))
                
                # parse byte array
                try:
                    fields = struct.unpack(key.structure,''.join([chr(c) for c in input]))                     
                except struct.error as err:
                    raise ParserException(
                            ParserException.DESERIALIZE,
                            "could not extract tuple {0} by applying {1} to {2}; error: {3}".format(
                                key.name,
                                key.structure,
                                u.formatBuf(input),
                                str(err)
                            )
                        )
                
                # map to name tuple
                returnTuple = self.named_tuple[key.name](*fields)
                
                # log
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("parsed into {0}".format(returnTuple))
                
                # map to name tuple
                return 'status', returnTuple
        
        # if you get here, no key was found
        raise ParserException(ParserException.NO_KEY, "type={0} (\"{1}\")".format(
            input[0],
            chr(input[0])))
    
    #======================== private =========================================
    
    def _addFieldsParser(self,index=None,val=None,name=None,structure=None,fields=None):
    
        # add to fields parsing keys
        self.fieldsParsingKeys.append(FieldParsingKey(index,val,name,structure,fields))
        
        # define named tuple
        self.named_tuple[name] = collections.namedtuple("Tuple_"+name, fields)