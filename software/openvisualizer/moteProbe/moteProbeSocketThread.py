import threading
import socket

class moteProbeSocketThread(threading.Thread):
    
    def __init__(self,socketport):
    
        # store params
        self.socketport      = socketport
        
        # local variables
        self.socket          = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn            =  None
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'moteProbeSocketThread@'+str(self.socketport)
    
    def run(self):
        self.socket.bind(('',self.socketport)) # attach to a socket on whatever IPv4 address of the computer
        self.socket.listen(1)                  # listen for incoming connection requests from the OpenVisualizer
        while True:
            # wait for OpenVisualizer to connect
            self.conn,self.addr = self.socket.accept()
            # record that I'm connected now
            print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+': openVisualizer connection from '+str(self.addr)
            # read data sent from OpenVisualizer
            while True:
                try:
                    bytesReceived = self.conn.recv(4096)
                    self.otherThreadHandler.send(bytesReceived)
                except socket.error:
                    print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+': openVisualizer disconnected'
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