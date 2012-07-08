import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('lbrClient')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
from moteConnector import MoteConnectorConsumer
import socket
import copy

class lbrClientMoteConnectorConsumer(MoteConnectorConsumer.MoteConnectorConsumer):
    
    def __init__(self,moteConnector):
        
        # log
        log.debug("create instance")
        
        # store params
        self.moteConnector   = moteConnector
        
        # initialize parent class
        MoteConnectorConsumer.MoteConnectorConsumer.__init__(self,self.moteConnector,
                                                                  [self.moteConnector.TYPE_DATA],
                                                                  self._receivedData_notif)
    
    def _receivedData_notif(self,data):
        print "lbrClientMoteConnectorConsumer data={0}".format(data)

class lbrClient(threading.Thread):
    
    STATUS_DISCONNECTED      = 'disconnected'
    STATUS_CONNECTING        = 'connecting'
    STATUS_AUTHENTICATING    = 'authenticating'
    STATUS_CONNECTED         = 'connected'
    
    AUTHTIMEOUT              = 5.0
    
    def __init__(self,moteConnector):
    
        # store params
        self.moteConnector   = moteConnector
        
        # log
        log.debug("creating instance")
        
        # local variables
        self.statsLock            = threading.Lock()
        self.stats                = {}
        self.connectSem           = threading.Lock()
        self.connectorConsumer    = lbrClientMoteConnectorConsumer(self.moteConnector)
        
        # reset the statistics
        self._resetStats()
        
        # acquire the connectSem, so the thread doesn't start listening
        self.connectSem.acquire()
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'lbrClient'
    
    def run(self):
        
        # log
        log.debug("starting to run")
        
        #start the moteConnectorConsumer
        self.connectorConsumer.start()
        
        while True:
            # reset the statistics
            self._resetStats()
            
            # wait to be connected
            self.connectSem.acquire()
            self.connectSem.release()
            
            # log
            log.debug("starting to listen for data")
            
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
                    
                    # look for the connected mote which is a bridge
                    self.moteConnector.write(input)
            
            except socket.error as err:
               
               # disconnect
               self.disconnect("socket error while listening: {0}".format(err))
    
    #======================== public ==========================================
    
    def connect(self,lbrAddr,lbrPort,netname):
        
        # log
        log.debug("connecting to {2}@{0}:{1}".format(lbrAddr,lbrPort,netname))
        
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
        
        if (len(input)!=20 or
            input[0]!='P'):
            
            # disconnect
            self.disconnect('Invalid prefix information from LBR')
            
            # abort connection
            return
            
        # no socket timeout from now on
        self.socket.settimeout(None)
        
        # record prefix
        self._storePrefix(input[1:])
        
        # update status
        self._updateStatus(self.STATUS_CONNECTED)
    
    def disconnect(self,reason):
        
        # log
        log.info('disconnecting: {0}'.format(reason))
        
        # acquire te connectSem so the listening stops
        if self._isConnected():
            self.connectSem.acquire()
        
        # reset the statistics (includes setting to disconnected)
        self._resetStats()
        
        # close the TCP session
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
    
    def _receivedData_notif(self,data):
        print data
    
    def send(self,lowpan):
        try:
            if self._isConnected():
                self.socket.send(chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+lowpan)
                
                # increment statistics
                self._incrementStats('sentPackets')
                self._incrementStats('sentBytes', step=len(lowpan)+8)
                
        except socket.error as err:
            log.error('socket error while sending: {0}'.format(err))
    
    def getStats(self):
        self.statsLock.acquire()
        returnVal = copy.deepcopy(self.stats)
        self.statsLock.release()
        
        return returnVal
    
    #======================== private =========================================
    
    def _resetStats(self):
        
        # log
        log.debug("resetting stats")
        
        self.statsLock.acquire()
        self.stats['status']           = self.STATUS_DISCONNECTED
        self.stats['lbrAddr']          = None
        self.stats['lbrPort']          = None
        self.stats['netname']          = None
        self.stats['prefix']           = None
        self.stats['sentPackets']      = 0
        self.stats['sentBytes']        = 0
        self.stats['receivedPackets']  = 0
        self.stats['receivedBytes']    = 0
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
        assert (statsName in ['receivedPackets',
                              'receivedBytes',
                              'sentPackets',
                              'sentBytes'])
        
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
