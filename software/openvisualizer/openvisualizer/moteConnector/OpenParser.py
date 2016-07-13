# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('OpenParser')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

from ParserException import ParserException
import Parser
import ParserStatus
import ParserInfoErrorCritical as ParserIEC
import ParserData
import ParserPacket

class OpenParser(Parser.Parser):
    
    HEADER_LENGTH  = 1
    
    SERFRAME_MOTE2PC_DATA              = ord('D')
    SERFRAME_MOTE2PC_STATUS            = ord('S')
    SERFRAME_MOTE2PC_INFO              = ParserIEC.ParserInfoErrorCritical.SEVERITY_INFO
    SERFRAME_MOTE2PC_ERROR             = ParserIEC.ParserInfoErrorCritical.SEVERITY_ERROR
    SERFRAME_MOTE2PC_CRITICAL          = ParserIEC.ParserInfoErrorCritical.SEVERITY_CRITICAL
    SERFRAME_MOTE2PC_REQUEST           = ord('R')
    SERFRAME_MOTE2PC_SNIFFED_PACKET    = ord('P')
    
    SERFRAME_PC2MOTE_SETDAGROOT        = ord('R')
    SERFRAME_PC2MOTE_DATA              = ord('D')
    SERFRAME_PC2MOTE_TRIGGERSERIALECHO = ord('S')
    SERFRAME_PC2MOTE_COMMAND           = ord('C')
    
    SERFRAME_ACTION_YES                = ord('Y')
    SERFRAME_ACTION_NO                 = ord('N')
    SERFRAME_ACTION_TOGGLE             = ord('T')
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        # subparser objects
        self.parserStatus    = ParserStatus.ParserStatus()
        self.parserInfo      = ParserIEC.ParserInfoErrorCritical(self.SERFRAME_MOTE2PC_INFO)
        self.parserError     = ParserIEC.ParserInfoErrorCritical(self.SERFRAME_MOTE2PC_ERROR)
        self.parserCritical  = ParserIEC.ParserInfoErrorCritical(self.SERFRAME_MOTE2PC_CRITICAL)
        self.parserData      = ParserData.ParserData()
        self.parserPacket    = ParserPacket.ParserPacket()
        
        # register subparsers
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_DATA,
            parser = self.parserData.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_STATUS,
            parser = self.parserStatus.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_INFO,
            parser = self.parserInfo.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_ERROR,
            parser = self.parserError.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_CRITICAL,
            parser = self.parserCritical.parseInput,
        )
        self._addSubParser(
            index  = 0,
            val    = self.SERFRAME_MOTE2PC_SNIFFED_PACKET,
            parser = self.parserPacket.parseInput,
        )
    #======================== public ==========================================
    
    #======================== private =========================================