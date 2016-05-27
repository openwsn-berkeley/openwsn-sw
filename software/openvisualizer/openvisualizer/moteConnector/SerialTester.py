# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('SerialTester')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import socket
import random
import traceback
import sys
import openvisualizer.openvisualizer_utils as u

from openvisualizer.eventBus      import eventBusClient
from openvisualizer.moteConnector import OpenParser

class SerialTester(eventBusClient.eventBusClient):
    
    DFLT_TESTPKT_LENGTH = 10  ##< number of bytes in a test packet
    DFLT_NUM_TESTPKT    = 20  ##< number of test packets to send
    DFLT_TIMEOUT        = 5   ##< timeout in second for getting a reply
    
    def __init__(self,moteProbeSerialPort):
        
        # log
        log.info("creating instance")
        
        # store params
        self.moteProbeSerialPort  = moteProbeSerialPort
        
        # local variables
        self.dataLock             = threading.RLock()
        self.testPktLen           = self.DFLT_TESTPKT_LENGTH
        self.numTestPkt           = self.DFLT_NUM_TESTPKT
        self.timeout              = self.DFLT_TIMEOUT
        self.traceCb              = None
        self.busyTesting          = False
        self.lastSent             = []
        self.lastReceived         = []
        self.waitForReply         = threading.Event()
        self._resetStats()
        
        # give this thread a name
        self.name = 'SerialTester@{0}'.format(self)
        
        # initialize parent 
        eventBusClient.eventBusClient.__init__(
            self,
            name             = self.name,
            registrations =  [
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'fromMoteProbe@'+self.moteProbeSerialPort,
                    'callback' : self._receiveDataFromMoteSerial,
                },
            ]
        )
        
    def quit(self):
        self.goOn = False
    
    #======================== public ==========================================
    
    def _receiveDataFromMoteSerial(self,sender,signal,data):
        
        # handle data
        if chr(data[0])==chr(OpenParser.OpenParser.SERFRAME_MOTE2PC_DATA):
            # don't handle if I'm not testing
            with self.dataLock:
                if not self.busyTesting:
                    return
            with self.dataLock:
               self.lastReceived = data[1+2+5:] # type (1B), moteId (2B), ASN (5B)
               # wake up other thread
               self.waitForReply.set()
    
    #===== setup test
    
    def setTestPktLength(self,newLength):
        assert type(newLength)==int
        with self.dataLock:
            self.testPktLen  = newLength
    
    def setNumTestPkt(self,newNum):
        assert type(newNum)==int
        with self.dataLock:
            self.numTestPkt  = newNum
    
    def setTimeout(self,newTimeout):
        assert type(newTimeout)==int
        with self.dataLock:
            self.timeout     = newTimeout
    
    def setTrace(self,newTraceCb):
        assert (callable(newTraceCb)) or (newTraceCb is None)
        with self.dataLock:
            self.traceCb     = newTraceCb
    
    #===== run test
    
    def test(self,blocking=True):
        if blocking:
            self._runtest()
        else:
            threading.Thread(target=self._runtest).start()
    
    #===== get test results
    
    def getStats(self):
        returnVal = None
        with self.dataLock:
            returnVal = self.stats.copy()
        return returnVal
    
    #======================== private =========================================
    
    def _runtest(self):
        
        # I'm testing
        with self.dataLock:
            self.busyTesting = True
            
        # gather test parameters
        with self.dataLock:
            testPktLen = self.testPktLen
            numTestPkt = self.numTestPkt
            timeout    = self.timeout
        
        # reset stats
        self._resetStats()
        
        # send packets and collect stats
        for i in range(numTestPkt):
            
            # prepare random packet to send
            packetToSend = [random.randint(0x00,0xff) for _ in range(testPktLen)]
            
            # remember as last sent packet
            with self.dataLock:
                self.lastSent = packetToSend[:]
            
            # send
            self.dispatch(
                signal        = 'fromMoteConnector@'+self.moteProbeSerialPort,
                data          = ''.join(
                    [chr(OpenParser.OpenParser.SERFRAME_PC2MOTE_TRIGGERSERIALECHO)]+[chr(b) for b in packetToSend]
                )
            )
            
            with self.dataLock:
                self.stats['numSent']                 += 1
            
            # log
            self._log('sent:     {0}'.format(self.formatList(self.lastSent)))
            
            # wait for answer
            self.waitForReply.clear()
            if self.waitForReply.wait(timeout):
                
                # log
                self._log('received: {0}'.format(self.formatList(self.lastReceived)))
                
                # echo received
                with self.dataLock:
                    if self.lastReceived==self.lastSent:
                        self.stats['numOk']           += 1
                    else:
                        self.stats['numCorrupted']    += 1
                        self._log('!! corrupted.')
            else:
                # timeout
                with self.dataLock:
                    self.stats['numTimeout']          += 1
                    self._log('!! timeout.')
        
        # I'm not testing
        with self.dataLock:
            self.busyTesting = False
    
    def _log(self,msg):
        if log.isEnabledFor(logging.DEBUG):
            log.debug(msg)
        with self.dataLock:
            if self.traceCb:
                self.traceCb(msg)
    
    def _resetStats(self):
        with self.dataLock:
            self.stats                = {
                'numSent'             : 0,
                'numOk'               : 0,
                'numCorrupted'        : 0,
                'numTimeout'          : 0,
            }
    
    def formatList(self,l):
        return '-'.join(['%02x'%b for b in l])