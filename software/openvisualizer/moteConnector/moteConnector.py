import threading
import socket
#from   processing import openRecord

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class moteConnector(threading.Thread):
    
    def __init__(self,moteProbeIp,moteProbeTcpPort):
    
        # store params
        self.moteProbeIp          = moteProbeIp
        self.moteProbeTcpPort     = moteProbeTcpPort
        
        # local variables
        self.socket               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
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
                    input = self.socket.recv(1024)
                    print "TODO pass to openRecord"
                    #openRecord.parseInput((self.moteProbeIp,self.moteProbeTcpPort),input)
            except socket.error as err:
                log.error(err)
                pass
    
    #======================== public ==========================================
    
    def write(self,stringToWrite):
        try:
            self.socket.send(stringToWrite)
        except socket.error:
            log.error(err)
            pass
    
    #======================== private =========================================