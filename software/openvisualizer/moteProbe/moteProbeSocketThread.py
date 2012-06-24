import threading
import socket

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbeSocketThread')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class moteProbeSocketThread(threading.Thread):
    
    def __init__(self,socketport):
        
        # log
        log.debug("create instance")
        
        # store params
        self.socketport      = socketport
        
        # local variables
        self.socket          = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn            = None
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'moteProbeSocketThread@'+str(self.socketport)
    
    def run(self):
        
        # log
        log.debug("start running")
        
        # attach to a socket on all interfaces of the computer
        self.socket.bind(('',self.socketport))
        
        # listen for incoming connection requests
        self.socket.listen(1)
        
        while True:
            # wait for OpenVisualizer to connect
            self.conn,self.addr = self.socket.accept()
            
            # log
            log.info("openVisualizer connection from {0}".format(self.addr))
            
            # read data sent from OpenVisualizer
            while True:
                
                try:
                    bytesReceived = self.conn.recv(4096)
                    self.otherThreadHandler.send(bytesReceived)
                except socket.error as err:
                
                    # log
                    log.info("openVisualizer disconnected")
                    
                    self.conn = None
                    break
    
    #======================== public ==========================================
    
    def setOtherThreadHandler(self,otherThreadHandler):
        self.otherThreadHandler = otherThreadHandler
    
    def send(self,bytesToSend):
        if self.conn!=None:
            try:
                self.conn.send(bytesToSend)
            except socket.error:
                # happens when not connected
                pass
    
    #======================== private =========================================