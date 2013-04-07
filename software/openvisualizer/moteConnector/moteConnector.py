import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket

from pydispatch import dispatcher

import OpenParser
import ParserException

class moteConnector(threading.Thread):
    
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
        
        # connect to dispatcher
        dispatcher.connect(
            self._updateConnectedToDagRoot,
            signal='infoDagRoot',
        )
        
    def run(self):
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
                        dispatcher.send(
                            signal        = 'fromMote.'+eventSubType,
                            sender        = self.name,
                            data          = parsedNotif,
                        )
                
            except socket.error as err:
                log.error(err)
                pass
    
    #======================== public ==========================================
    
    def _updateConnectedToDagRoot(self,data):
        if  (
               (self.moteProbeIp==data['ip'])
               and
               (self.moteProbeTcpPort==data['tcpPort'])
            ):
            # this moteConnector is connected to a DAGroot
            
            if not self._subcribedDataForDagRoot:
                
                # connect to dispatcher
                dispatcher.connect(
                    self.write,
                    signal='bytesToMesh',
                )
                
                self._subcribedDataForDagRoot = True
            
        else:
            # this moteConnector is *not* connected to a DAGroot
            
            if self._subcribedDataForDagRoot:
                # disconnect from dispatcher
                dispatcher.disconnect(
                    self.write,
                    signal='bytesToMesh',
                )
                
                self._subcribedDataForDagRoot = False
    
    def write(self,data,headerByte=chr(OpenParser.OpenParser.SERFRAME_MOTE2PC_DATA)):
        try:
            self.socket.send(headerByte+data)
        except socket.error:
            log.error(err)
            pass
    
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================