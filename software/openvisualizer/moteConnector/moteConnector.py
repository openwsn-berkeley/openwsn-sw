import threading
import socket

import OpenParser
import ParserException

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class moteConnectorRegistree(object):
    def __init__(self,filter,cb):
        self.filter = filter
        self.cb     = cb

class moteConnector(threading.Thread):
    
    TYPE_STATUS    = OpenParser.OpenParser.TYPE_STATUS
    TYPE_ERROR     = OpenParser.OpenParser.TYPE_ERROR
    TYPE_DATA      = OpenParser.OpenParser.TYPE_DATA
    
    def __init__(self,moteProbeIp,moteProbeTcpPort):
    
        # store params
        self.moteProbeIp          = moteProbeIp
        self.moteProbeTcpPort     = moteProbeTcpPort
        
        # local variables
        self.socket               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parser               = OpenParser.OpenParser()
        self.dataLock             = threading.Lock()
        self.registrees           = []
        
        # log
        log.debug("connecting to moteProbe@{0}:{1}".format(self.moteProbeIp,self.moteProbeTcpPort))
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'moteConnector to {0}:{1}'.format(self.moteProbeIp,self.moteProbeTcpPort)
    
    def run(self):
        # log
        log.debug("starting to run")
    
        while True:
            try:
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
                        (notifType,parsedNotif)  = self.parser.parseInput(input)
                    except ParserException as err:
                        # log
                        log.warning(str(err))
                        # report as parsedNotif
                        parsedNotif    = err
                    
                    # inform all registrees
                    self.dataLock.acquire()
                    for registree in self.registrees:
                        if notifType in registree.filter:
                            registree.cb(parsedNotif)
                    self.dataLock.release()
                    
            except socket.error as err:
                log.error(err)
                pass
    
    #======================== public ==========================================
    
    def register(self,filter,cb):
        self.dataLock.acquire()
        self.registrees.append(moteConnectorRegistree(filter,cb))
        self.dataLock.release()
    
    def write(self,stringToWrite):
        try:
            self.socket.send(stringToWrite)
        except socket.error:
            log.error(err)
            pass
    
    #======================== private =========================================