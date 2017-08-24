# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('moteConnector')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import socket
import traceback
import sys
import binascii
import openvisualizer.openvisualizer_utils as u

from pydispatch import dispatcher

from openvisualizer.eventBus      import eventBusClient
from openvisualizer.moteState     import moteState

import OpenParser
import ParserException

class moteConnector(eventBusClient.eventBusClient):
    
    def __init__(self,serialport):
        
        # log
        log.info("creating instance")
        
        # store params
        self.serialport                = serialport
        
        # local variables
        self.parser                    = OpenParser.OpenParser()
        self.stateLock                 = threading.Lock()
        self.networkPrefix             = None
        self._subcribedDataForDagRoot  = False
              
        # give this thread a name
        self.name = 'moteConnector@{0}'.format(self.serialport)
       
        eventBusClient.eventBusClient.__init__(
            self,
            name             = self.name,
            registrations =  [
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'infoDagRoot',
                    'callback' : self._infoDagRoot_handler,
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'cmdToMote',
                    'callback' : self._cmdToMote_handler,
                },
            ]
        )
        
        # subscribe to dispatcher
        dispatcher.connect(
            self._sendToParser,
            signal = 'fromMoteProbe@'+self.serialport,
        )
        
    def _sendToParser(self,data):
        
        input = data
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("received input={0}".format(input))
        
        # parse input
        try:
            (eventSubType,parsedNotif)  = self.parser.parseInput(input)
            assert isinstance(eventSubType,str)
        except ParserException.ParserException as err:
            # log
            log.error(str(err))
            pass
        else:
            # dispatch
            self.dispatch('fromMote.'+eventSubType,parsedNotif)
        
    #======================== eventBus interaction ============================
    
    def _infoDagRoot_handler(self,sender,signal,data):
        
        # I only care about "infoDagRoot" notifications about my mote
        if not data['serialPort']==self.serialport:
            return 
        
        with self.stateLock:
        
            if   data['isDAGroot']==1 and (not self._subcribedDataForDagRoot):
                # this moteConnector is connected to a DAGroot
                
                # connect to dispatcher
                self.register(
                    sender   = self.WILDCARD,
                    signal   = 'bytesToMesh',
                    callback = self._bytesToMesh_handler,
                )
                
                # remember I'm subscribed
                self._subcribedDataForDagRoot = True
                
            elif data['isDAGroot']==0 and self._subcribedDataForDagRoot:
                # this moteConnector is *not* connected to a DAGroot
                
                # disconnect from dispatcher
                self.unregister(
                    sender   = self.WILDCARD,
                    signal   = 'bytesToMesh',
                    callback = self._bytesToMesh_handler,
                )
                
                # remember I'm not subscribed
                self._subcribedDataForDagRoot = False
    
    def _cmdToMote_handler(self,sender,signal,data):
        if  data['serialPort']==self.serialport:
            if data['action']==moteState.moteState.TRIGGER_DAGROOT:
                
                # retrieve the prefix of the network
                with self.stateLock:
                    if not self.networkPrefix:
                        networkPrefix = self._dispatchAndGetResult(
                            signal       = 'getNetworkPrefix',
                            data         = [],
                        )
                        self.networkPrefix = networkPrefix
                
                # retrieve the security key of the network
                with self.stateLock:
                    keyDict = self._dispatchAndGetResult(
                            signal       = 'getL2SecurityKey',
                            data         = [],
                    )
    
                # create data to send
                with self.stateLock:
                    dataToSend = [
                        OpenParser.OpenParser.SERFRAME_PC2MOTE_SETDAGROOT,
                        OpenParser.OpenParser.SERFRAME_ACTION_TOGGLE,
                    ]+self.networkPrefix+keyDict['index']+keyDict['value']
                
                # toggle the DAGroot state
                self._sendToMoteProbe(
                    dataToSend = dataToSend,
                )
            elif data['action'][0]==moteState.moteState.SET_COMMAND:
                # this is command for golden image
                with self.stateLock:
                    [success,dataToSend] = self._commandToBytes(data['action'][1:])

                if not success:
                    return

                # print dataToSend
                # send command to GD image
                self._sendToMoteProbe(
                    dataToSend = dataToSend,
                )
            else:
                raise SystemError('unexpected action={0}'.format(data['action']))
    
    def _commandToBytes(self,data):
        
        # data[0]: commandID
        # data[1]: parameter

        outcome    = False
        dataToSend = []
        ptr        = 0

        # get commandId
        commandIndex = 0
        for cmd in moteState.moteState.COMMAND_ALL:
            if data[0] == cmd[0]:
                commandId  = cmd[1]
                commandLen = cmd[2]
                break
            else:
                commandIndex += 1

        # check avaliability of command
        if commandIndex == len(moteState.moteState.COMMAND_ALL):
            print "============================================="
            print "Wrong Command Type! Available Command Type: {"
            for cmd in moteState.moteState.COMMAND_ALL:
                print " {0}".format(cmd[0])
            print " }"
            return [outcome,dataToSend]

        if data[0][:2] == '6p':
            try:
                dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_COMMAND,
                    commandId,
                    commandLen
                ]
                paramList = data[1].split(',')
                if data[0] != '6pClear':
                    if paramList[0] == 'tx':
                        cellOptions = 1<<0
                    elif paramList[0] == 'rx':
                        cellOptions = 1<<1
                    elif paramList[0] == 'shared':
                        cellOptions = 1<<0 | 1<<1 | 1<<2
                    else:
                        print "unsupport cellOptions!"
                        assert TRUE
                else:
                    dataToSend[2] = len(dataToSend)-3
                    outcome       = True
                    return [outcome,dataToSend]
                ptr += 1
                dataToSend  += [cellOptions]
                celllist_add    = {}
                celllist_delete = {}
                if data[0] == '6pList'  and len(paramList)==3:
                    dataToSend += map(int,paramList[ptr:])
                if data[0] == '6pAdd':
                    # append numCell
                    dataToSend += [int(paramList[ptr])]
                    # append celllist
                    celllist_add['slotoffset']    = paramList[ptr+1].split('-')
                    celllist_add['channeloffset'] = paramList[ptr+2].split('-')
                    if len(celllist_add['slotoffset']) != len(celllist_add['channeloffset']) or len(celllist_add['slotoffset']) < int(paramList[ptr]):
                        print "the length of slotoffset list and channeloffset list for candidate cell should be equal!"
                        assert TRUE
                    dataToSend += map(int,celllist_add['slotoffset'])
                    dataToSend += map(int,celllist_add['channeloffset'])
                if data[0] == '6pDelete':
                    # append numCell
                    dataToSend += [int(paramList[ptr])]
                    # append celllist
                    celllist_delete['slotoffset']    = paramList[ptr+1].split('-')
                    celllist_delete['channeloffset'] = paramList[ptr+2].split('-')
                    if int(paramList[ptr]) != len(celllist_delete['slotoffset']) or int(paramList[ptr]) != len(celllist_delete['channeloffset']):
                        print "length of celllist (slotoffset/channeloffset) to delete doesn't match numCell!"
                        assert TRUE
                    dataToSend += map(int,celllist_delete['slotoffset'])
                    dataToSend += map(int,celllist_delete['channeloffset'])
                if data[0] == '6pRelocate':
                    dataToSend += [int(paramList[ptr])]
                    # append celllist
                    celllist_delete['slotoffset']    = paramList[ptr+1].split('-')
                    celllist_delete['channeloffset'] = paramList[ptr+2].split('-')
                    if int(paramList[ptr]) != len(celllist_delete['slotoffset']) or int(paramList[ptr]) != len(celllist_delete['channeloffset']):
                        print "length of celllist (slotoffset/channeloffset) to delete doesn't match numCell!"
                        assert TRUE
                    dataToSend += map(int,celllist_delete['slotoffset'])
                    dataToSend += map(int,celllist_delete['channeloffset'])
                    ptr += 3
                    # append celllist
                    celllist_add['slotoffset']    = paramList[ptr].split('-')
                    celllist_add['channeloffset'] = paramList[ptr+1].split('-')
                    if len(celllist_add['slotoffset']) != len(celllist_add['channeloffset']) or len(celllist_add['slotoffset']) < len(celllist_delete['slotoffset']):
                        print "the length of slotoffset list and channeloffset list for candidate cell should be equal and the length of candidate celllist must no less than numCell!"
                        assert TRUE
                    dataToSend += map(int,celllist_add['slotoffset'])
                    dataToSend += map(int,celllist_add['channeloffset'])
                dataToSend[2] = len(dataToSend)-3
                outcome       = True
                return [outcome,dataToSend]
            except:
                print "============================================="
                print "Wrong 6p parameter format."
                print "                           command    cellOptions numCell     celllist_delete         celllist_add       listoffset maxListLen addition"
                print "                                                          (slotlist,channellist)  (slotlist,channellist)"
                print "comma. e.g. set <portname> 6pAdd      tx,         1,                                  5-6-7,4-4-4"
                print "comma. e.g. set <portname> 6pDelete   rx,         1,              5,4"
                print "comma. e.g. set <portname> 6pRelocate tx,         1,              5,4,                6-7-8,4-4-4"
                print "comma. e.g. set <portname> 6pCount    shared"
                print "comma. e.g. set <portname> 6pList     tx,                                                                 5,         3"
                print "comma. e.g. set <portname> 6pClear                                                                                              all"
                return [outcome,dataToSend]
        elif data[0] == 'joinKey':
            try:
                if len(data[1]) != commandLen*2: # two hex chars is one byte
                    raise ValueError
                payload = binascii.unhexlify(data[1])
                dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_COMMAND,
                    commandId,
                    commandLen,
                ]
                dataToSend += [ord(b) for b in payload]
            except:
                print "============================================="
                print "Wrong joinKey format. Input 16-byte long hex string. e.g. cafebeefcafebeefcafebeefcafebeef"
        else:
            parameter = int(data[1])
            if parameter <= 0xffff:
                parameter  = [(parameter & 0xff),((parameter >> 8) & 0xff)]
                dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_COMMAND,
                    commandId,
                    commandLen, # length 
                    parameter[0],
                    parameter[1]
                ]
            else:
                # more than two bytes parameter, error
                print "============================================="
                print "Paramter Wrong! (Available: 0x0000~0xffff)\n"
                return [outcome,dataToSend]

        # the command is legal if I got here
        dataToSend[2] = len(dataToSend)-3
        outcome       = True
        return [outcome,dataToSend]


    def _bytesToMesh_handler(self,sender,signal,data):
        assert type(data)==tuple
        assert len(data)==2
        
        (nextHop,lowpan) = data
        
        self._sendToMoteProbe(
            dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_DATA]+nextHop+lowpan,
        )
    
    #======================== public ==========================================
    
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================
    
    def _sendToMoteProbe(self,dataToSend):
        try:
             dispatcher.send(
                      sender        = self.name,
                      signal        = 'fromMoteConnector@'+self.serialport,
                      data          = ''.join([chr(c) for c in dataToSend])
                      )
            
        except socket.error:
            log.error(err)
            pass