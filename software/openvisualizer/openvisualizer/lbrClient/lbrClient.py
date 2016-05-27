# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('lbrClient')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import copy
import socket
import threading
import traceback
import sys
import openvisualizer.openvisualizer_utils as u

from pydispatch import dispatcher
from openvisualizer.eventBus import eventBusClient


class lbrClient(threading.Thread):
    
    STATUS_DISCONNECTED      = 'disconnected'
    STATUS_CONNECTING        = 'connecting'
    STATUS_AUTHENTICATING    = 'authenticating'
    STATUS_CONNECTED         = 'connected'
    
    AUTHTIMEOUT              = 5.0
    
    def __init__(self):
    
        # store params
        
        # log
        log.info("creating instance")
        
        # local variables
        self.statsLock            = threading.Lock()
        self.stats                = {}
        self.connectSem           = threading.Lock()
        self.eventBusClient       = eventBusClient.eventBusClient(
            name          = 'lbrClient',
            signal        = 'fromMote.data.internet',
            sender        = dispatcher.Any,
            notifCallback = self.send,
        )
        
        # reset the statistics
        self._resetStats()
        
        # acquire the connectSem, so the thread doesn't start listening
        self.connectSem.acquire()
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'lbrClient'
    
    def run(self):
        try:
            # log
            log.info("starting to run")
            
            #start the eventBusClient
            self.eventBusClient.start()
            
            while True:
                # reset the statistics
                self._resetStats()
                
                # wait to be connected
                self.connectSem.acquire()
                self.connectSem.release()
                
                # log
                log.info("starting to listen for data")
                
                try:
                    while True:
                        
                        # wait for some data
                        input = self.socket.recv(4096)
                        
                        # disconnect if needed
                        if not input:
                            if self._isConnected():
                                self.disconnect("No input.")
                            break
                        
                        # increment statistics
                        self._incrementStats('receivedPackets')
                        self._incrementStats('receivedBytes', step=len(input))
                        
                        # handle received data
                        # the data received from the LBR should be:
                        # - first 8 bytes: EUI64 of the final destination
                        # - remainder: 6LoWPAN packet and above
                        if len(input)<8:
                            log.error("received packet from LBR which is too short ({0} bytes)".format(len(input)))
                            continue
                        
                        # dispatch the packet to network state to figure out source route.
                        dispatcher.send(
                            sender        = 'lbrClient',
                            signal        = 'lowpanToMesh',
                            data          = input,
                        )
                
                except socket.error as err:
                   
                   # disconnect
                   self.disconnect("socket error while listening: {0}".format(err))
        except Exception as err:
            errMsg=u.formatCrashMessage(self.name,err)
            print errMsg
            log.critical(errMsg)
            sys.exit(1)
            
                    
            
            
    #======================== public ==========================================
    
    def connect(self,lbrAddr,lbrPort,netname):
        
        # log
        log.info("connecting to {2}@{0}:{1}".format(lbrAddr,lbrPort,netname))
        
        #test source routing:
        #self.timer = threading.Timer(20,self._testSourceRouting)
        #self.timer.start()
        
        # store connection params
        self._updateConnectParams(lbrAddr,lbrPort,netname)
        
        # update status
        self._updateStatus(self.STATUS_CONNECTING)
        
        # create TCP socket to connect to LBR
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self._getConnectParam('lbrAddr'),
                                 self._getConnectParam('lbrPort')))
        except socket.error:
            
            # disconnect
            self.disconnect('Could not open socket to LBR@{0}:{1}'.format(
                self._getConnectParam('lbrAddr'),
                self._getConnectParam('lbrPort')))
            
            # abort connection
            return
        
        # update status
        self._updateStatus(self.STATUS_AUTHENTICATING)
        
        self.socket.settimeout(self.AUTHTIMEOUT) # listen for at most AUTHTIMEOUT seconds
        
        # ---S---> send security capability
        self.socket.send('S'+chr(0))
        
        # <---S--- listen for (same) security capability
        try:
            input = self.socket.recv(4096)
        except socket.timeout:
        
            # disconnect
            self.disconnect('Waited too long for security reply')
            
            # abort connection
            return
        
        if (len(input)!=2   or
            input[0]  !='S' or
            input[1]  !=chr(0)):
            
            # disconnect
            self.disconnect('Incorrect security reply from LBR')
            
            # abort connection
            return
        
        # ---N---> send netname
        self.socket.send('N'+self._getConnectParam('netname'))
        
        # <--N---- receive netname
        try:
            input = self.socket.recv(4096)
        except socket.timeout:
            
            # disconnect
            self.disconnect('Waited too long for netname')
            
            # abort connection
            return
        
        # <---P--- listen for prefix
        try:
            input = self.socket.recv(4096)
        except socket.timeout:
            
            # disconnect
            self.disconnect('Waited too long for prefix')
            
            # abort connection
            return
        #the packet should be at least size 20 which is P+prefix 
        if len(input) < 20 or input[0]!= 'P':
            
            # disconnect
            self.disconnect('Invalid prefix information from LBR')
            
            # abort connection
            return
            
        # no socket timeout from now on
        self.socket.settimeout(None)
        
        # record prefix
        self._storePrefix(input[1:20])
        
        # update status
        self._updateStatus(self.STATUS_CONNECTED)
        
     
  
  
    def _testSourceRouting(self):
        pkt=[]
        #[0, 0, 0, 0, 0, 0, 0, 233]
        pkt=[20, 21, 146, 9, 2, 44, 0, 216] #destination address
        
        #pkt=[0, 0, 0, 0, 0, 0, 0, 233]
        
        for i in range (50):
            pkt.append(i)
            
        dispatcher.send(
            sender      = 'lbrClient',
            signal      = 'lowpanToMesh',
            data        = pkt,
        )
        #start the timer again
        #self.timer = threading.Timer(20,self._testSourceRouting)
        #self.timer.start()
              
    def disconnect(self,reason):
        
        # log
        log.info('disconnecting: {0}'.format(reason))
        
        # acquire te connectSem so the listening stops
        if self._isConnected():
            self.connectSem.acquire()
        
        # reset the statistics (includes setting to disconnected)
        self._resetStats(disconnectReason=reason)
        
        # close the TCP session
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
    
    # this is the callback executed by eventBusClient
    def send(self,lowpan):
        try:
            if self._isConnected():
                
                # add 8 bytes of 0
                lowpan = [0]*8 + lowpan
                
                # convert to string
                lowpan = ''.join([chr(b) for b in lowpan])
                printlowpan=''.join([str(b).encode("hex") for b in lowpan])
                # send to LBR
                self.socket.send(lowpan)
                
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('packet sent to lbr: {}'.format(printlowpan))
                
                # increment statistics
                self._incrementStats('packetsSentOk')
                self._incrementStats('bytesSentOk', step=len(lowpan))
            
            else:
                # increment statistics
                self._incrementStats('packetsSentFailed')
                self._incrementStats('bytesSentFailed', step=len(lowpan))
                
        except socket.error as err:
            log.error('socket error while sending: {0}'.format(err))
    
    def getStats(self):
        self.statsLock.acquire()
        returnVal = copy.deepcopy(self.stats)
        self.statsLock.release()
        
        return returnVal
    
    def getPrefix(self):
        self.statsLock.acquire()
        prefix = self.stats['prefix']
        self.statsLock.release()
        return prefix
    
    #======================== private =========================================
    
    #===== stats handling
    
    def _resetStats(self,disconnectReason=None):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("resetting stats")
        
        self.statsLock.acquire()
        self.stats['disconnectReason']      = disconnectReason
        self.stats['status']                = self.STATUS_DISCONNECTED
        self.stats['lbrAddr']               = None
        self.stats['lbrPort']               = None
        self.stats['netname']               = None
        self.stats['prefix']                = None
        self.stats['packetsSentOk']         = 0
        self.stats['bytesSentOk']           = 0
        self.stats['packetsSentFailed']     = 0
        self.stats['bytesSentFailed']       = 0
        self.stats['receivedPackets']       = 0
        self.stats['receivedBytes']         = 0
        self.statsLock.release()
    
    def _isConnected(self):
        self.statsLock.acquire()
        returnVal = (self.stats['status']==self.STATUS_CONNECTED)
        self.statsLock.release()
        
        return returnVal
    
    def _updateStatus(self,newStatus):
        assert (newStatus in [self.STATUS_DISCONNECTED,
                              self.STATUS_CONNECTING,
                              self.STATUS_AUTHENTICATING,
                              self.STATUS_CONNECTED])
        
        self.statsLock.acquire()
        self.stats['status'] = newStatus
        if newStatus==self.STATUS_CONNECTED:
            self.connectSem.release()
        self.statsLock.release()
    
    def _incrementStats(self,statsName,step=1):
        assert (statsName in ['packetsSentOk',
                              'bytesSentOk',
                              'packetsSentFailed',
                              'bytesSentFailed',
                              'receivedPackets',
                              'receivedBytes'])
        
        self.statsLock.acquire()
        self.stats[statsName] += step
        self.statsLock.release()
    
    def _updateConnectParams(self,lbrAddr,lbrPort,netname):
        
        self.statsLock.acquire()
        self.stats['lbrAddr'] = lbrAddr
        self.stats['lbrPort'] = lbrPort
        self.stats['netname'] = netname
        self.statsLock.release()
    
    def _getConnectParam(self,paramName):
        assert (paramName in ['lbrAddr','lbrPort','netname'])
        
        self.statsLock.acquire()
        returnVal = self.stats[paramName]
        self.statsLock.release()
        
        return returnVal
    
    def _storePrefix(self,prefix):
        
        self.statsLock.acquire()
        self.stats['prefix'] = prefix
        self.statsLock.release()
        
        # dispatch
        dispatcher.send(
            sender      = 'lbrClient',
            signal      = 'networkPrefix',
            data        = prefix,
        )
