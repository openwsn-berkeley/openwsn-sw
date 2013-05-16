import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket
import traceback
import sys
import openvisualizer_utils as u

from eventBus      import eventBusClient
from moteState     import moteState

import OpenParser
import ParserException

class moteConnector(threading.Thread,eventBusClient.eventBusClient):
    
    def __init__(self,moteProbeIp,moteProbeTcpPort):
        
        # log
        log.debug("creating instance")
        
        # store params
        self.moteProbeIp               = moteProbeIp
        self.moteProbeTcpPort          = moteProbeTcpPort
        
        # local variables
        self.socket                    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parser                    = OpenParser.OpenParser()
        self.goOn                      = True
        self._subcribedDataForDagRoot  = False
          
        # initialize parent class
      
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'moteConnector@{0}:{1}'.format(self.moteProbeIp,self.moteProbeTcpPort)
       
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
        
    def run(self):
        try:
            # log
            log.debug("starting to run")
        
            while self.goOn:
                try:
                    # log
                    log.debug("connecting to moteProbe@{0}:{1}".format(self.moteProbeIp,self.moteProbeTcpPort))
                    
                    # connect
                    self.socket.connect((self.moteProbeIp,self.moteProbeTcpPort))
                    while True:
                        # retrieve the string of bytes from the socket
                        inputString                  = self.socket.recv(1024)
                        
                        # convert to a byte array
                        input                        = [ord(c) for c in inputString]
                        
                        # log
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
                            
                    
                except socket.error as err:
                    log.error(err)
                    pass
        except Exception as err:
            errMsg=u.formatCrashMessage(self.name,err)
            print errMsg
            log.critical(errMsg)
            sys.exit(1)
        
    #======================== public ==========================================
    
    def _cmdToMote_handler(self,sender,signal,data):
        if  (
               (self.moteProbeIp==data['ip'])
               and
               (self.moteProbeTcpPort==data['tcpPort'])
            ):
            
            if data['action']==moteState.moteState.TRIGGER_DAGROOT:
                # toggle the DAGroot status
                self._sendToMoteProbe(
                    dataToSend = [
                        OpenParser.OpenParser.SERFRAME_PC2MOTE_SETROOT,
                        OpenParser.OpenParser.SERFRAME_ACTION_TOGGLE,
                    ],
                )
                # toggle the bridge status
                self._sendToMoteProbe(
                    dataToSend = [
                        OpenParser.OpenParser.SERFRAME_PC2MOTE_SETBRIDGE,
                        OpenParser.OpenParser.SERFRAME_ACTION_TOGGLE,
                    ],
                )
            else:
                raise SystemError('unexpected action={0}'.format(data['action']))
    
    def _infoDagRoot_handler(self,sender,signal,data):
        if  (
               (self.moteProbeIp==data['ip'])
               and
               (self.moteProbeTcpPort==data['tcpPort'])
            ):
            # this moteConnector is connected to a DAGroot
            
            if not self._subcribedDataForDagRoot:
                
                # connect to dispatcher
                self.register(
                    sender   = self.WILDCARD,
                    signal   = 'bytesToMesh',
                    callback = self._bytesToMesh_handler,
                )
                
                # remember I'm subscribed
                self._subcribedDataForDagRoot = True
            
        else:
            # this moteConnector is *not* connected to a DAGroot
            
            if self._subcribedDataForDagRoot:
                
                # disconnect from dispatcher
                self.unregister(
                    sender   = self.WILDCARD,
                    signal   = 'bytesToMesh',
                    callback = self._bytesToMesh_handler,
                )
                
                # remember I'm not subscribed
                self._subcribedDataForDagRoot = False
    
    def _bytesToMesh_handler(self,sender,signal,data):
        assert type(data)==tuple
        assert len(data)==2
        
        (nextHop,lowpan) = data
        
        self._sendToMoteProbe(
            dataToSend = [OpenParser.OpenParser.SERFRAME_PC2MOTE_DATA]+nextHop+lowpan,
        )
    
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================
    
    def _sendToMoteProbe(self,dataToSend):
        
        try:
            self.socket.send(''.join([chr(c) for c in dataToSend]))
        except socket.error:
            log.error(err)
            pass