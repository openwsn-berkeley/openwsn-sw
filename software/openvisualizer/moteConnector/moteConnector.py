import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket

import OpenParser
import ParserException
from   EventBus import EventBus

class moteConnector(threading.Thread):
    
    TYPE_STATUS    = OpenParser.OpenParser.TYPE_STATUS
    TYPE_ERROR     = OpenParser.OpenParser.TYPE_ERROR
    TYPE_DATA      = OpenParser.OpenParser.TYPE_DATA
    
    def __init__(self,moteProbeIp,moteProbeTcpPort):
        
        # log
        log.debug("creating instance")
        
        # store params
        self.moteProbeIp          = moteProbeIp
        self.moteProbeTcpPort     = moteProbeTcpPort
        
        # local variables
        self.socket               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parser               = OpenParser.OpenParser()
        self.goOn                 = True
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'moteConnector to {0}:{1}'.format(self.moteProbeIp,self.moteProbeTcpPort)
    
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
                        # publish on eventBus
                        EventBus.EventBus().publish(
                            'moteConnector.{0}:{1}.inputFromMoteProbe.{2}'.format(
                                self.moteProbeIp,
                                self.moteProbeTcpPort,
                                eventSubType
                            ),
                            parsedNotif,
                        )
                
            except socket.error as err:
                log.error(err)
                pass
    
    #======================== public ==========================================
    
    def write(self,stringToWrite,headerByte='D'):
        try:
            self.socket.send(headerByte+stringToWrite)
        except socket.error:
            log.error(err)
            pass
    
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================