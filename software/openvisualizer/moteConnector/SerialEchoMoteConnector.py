import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SerialEchoMoteConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket

import ParserException

class SerialEchoMoteConnector(threading.Thread):
    
    
    def __init__(self,moteProbeIp,moteProbeTcpPort):
        
        # log
        log.debug("creating instance")
        
        # store params
        self.moteProbeIp               = moteProbeIp
        self.moteProbeTcpPort          = moteProbeTcpPort
        
        # local variables
        self.socket                    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.goOn                      = True

        #lock to protect datasent var
        self.stateLock            = threading.Lock()
        self.dataSent             = []
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'serialEchoMoteConnector@{0}:{1}'.format(self.moteProbeIp,self.moteProbeTcpPort)
        
        
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
                    if (chr(input[0])=='D'):
                        log.debug("received input={0}".format(" ".join((chr(c) for c in input))))
                        print "received ={0}".format(" ".join(chr(c) for c in input))
                        #verify
                        result=self._checkWithSent(input[8:],self.dataSent)
                        
                        log.debug("input and output are equal = {0}".format(result))
                        print "input and output are equal = {0}".format(result);
                    
            except socket.error as err:
                log.error(err)
                pass
    
    #compares sent vs echo
    def _checkWithSent(self,input,sent):
        
        max=len(input)
        result=True
        i=0
        
        if (max > len(sent)):
            max=len(sent)
        
        for i in range(max):
            if (sent[i]!=input[i]):
                result = False
                log.debug("different elements at position ={0} , being sent={1}, received={2}".format(i,chr(sent[i]),chr(input[i])))
                print "different elements at position ={0} , being sent={1}, received={2}".format(i,chr(sent[i]),chr(input[i]))
                break
                        
        return result
        
    #======================== public ==========================================
    
    def write(self,data,headerByte='H'):
        try:
            
            with self.stateLock:
                self.dataSent  = [ord(c) for c in data] #keep it globally
                aux=headerByte+data
                
            self.socket.send(aux)
            log.debug("sent ={0}".format(" ".join(str(c) for c in aux)))
            print "sent ={0}".format(" ".join(str(c) for c in aux))
        except socket.error:
            log.error(err)
            pass
    
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================