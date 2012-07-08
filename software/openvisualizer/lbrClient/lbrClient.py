import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('lbrClient')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket
import binascii
import tkFileDialog
import tkMessageBox
import re

class lbrClient(threading.Thread):
    
    ## max number of seconds to wait for an authentication packet
    AUTHTIMEOUT = 5.0
    
    def __init__(self):
    
        # log
        log.debug("creating instance")
        
        self.varLock           = threading.Lock()
        self.isConnected       = False
        self.connectSem        = threading.Lock()
        self.connectSem.acquire()
        
        self.sentColor         = 'red'
        self.receivedColor     = 'red'
        threading.Thread.__init__(self)
        self.setName('lbrClientThread')
    
    def run(self):
        
        # log
        log.debug("starting to run")
        
        while True:
            self.resetStats()
            self.connectSem.acquire()
            self.connectSem.release()
            try:
                while True:
                    input = self.socket.recv(4096)
                    if not input:
                        self.varLock.acquire()
                        tempConnected = self.isConnected
                        self.varLock.release()
                        if tempConnected == True:
                            self.disconnect()
                        break
                    #update statistics
                    self.receivedPackets += 1
                    self.receivedBytes   += len(input)
                    # handle received data
                    # the data received from the LBR should be:
                    # - first 8 bytes: EUI64 of the final destination
                    # - remainder: 6LoWPAN packet and above
                    if len(input)<8:
                        print '[lbrClient] ERROR: received packet from LBR which is too short ('+str(len(input))+' bytes)'
                        print binascii.hexlify(input)
                        continue
                    # look for the connected mote which is a bridge
                    if shared.portBridgeMote!=None:
                        shared.moteConnectors[shared.portBridgeMote].write(input)
                    else:
                        if self.receivedColor=='red':
                            self.receivedColor = 'orange'
                        else:
                            self.receivedColor = 'red'
            except socket.error:
               print 'poipoipoipoi'
               self.disconnect()
    
    def resetStats(self):
        
        # log
        log.debug("resetting stats")
    
        self.prefix          = ''
        self.status          = 'disconnected'
        self.sentPackets     = 0
        self.sentBytes       = 0
        self.receivedPackets = 0
        self.receivedBytes   = 0
    
    def connect(self):
        # open authentication file
        authFile = tkFileDialog.askopenfile(mode='r',
                                            title = 'Select an LBR authentication file',
                                            multiple = False,
                                            initialfile = 'guest.lbrauth',
                                            filetypes = [("LBR authentication file", "*.lbrauth")] )
        # parse authentication file
        try:
            for line in authFile:
                match = re.search('(.*)=(.*)',line)
                if match!=None:
                    key = match.group(1).strip()
                    val = match.group(2).strip()
                    if   key=='LBRADDR':
                        self.lbrAddr = val
                    elif key=='LBRPORT':
                        self.lbrPort = int(val)
                    elif key=='NETNAME':
                        self.netname = val
            self.lbrAddr # this line makes sure this variable exists
            self.lbrPort # this line makes sure this variable exists
            self.netname # this line makes sure this variable exists
        except:
            tkMessageBox.showerror('Error','Misformed LBR authentication file.')
            return
        # update stats
        self.status          = 'connecting'
        # create TCP socket to connect to LBR
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.lbrAddr,self.lbrPort))
        except:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error:
                pass
            tkMessageBox.showerror('Error','Could not open socket to LBR@'+self.lbrAddr+':'+str(self.lbrPort))
            return
        # update stats
        self.status          = 'authenticating'
        self.socket.settimeout(self.AUTHTIMEOUT) # listen for at most AUTHTIMEOUT seconds
        # ---S---> send security capability
        self.socket.send('S'+chr(0))
        # <---S--- listen for (same) security capability
        try:
            input = self.socket.recv(4096)
        except socket.timeout:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error:
                pass
            tkMessageBox.showerror('Error','Waited too long for security reply')
            return
        if (len(input)!=2   or
            input[0]  !='S' or
            input[1]  !=chr(0)):
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error:
                pass
            tkMessageBox.showerror('Error','Incorrect security reply from LBR')
            return
        # ---N---> send netname
        self.socket.send('N'+self.netname)
        try:
            input = self.socket.recv(4096)
        except socket.timeout:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error:
                pass
            tkMessageBox.showerror('Error','Waited too long for netname')
            return
        # <---P--- listen for prefix
        try:
            input = self.socket.recv(4096)
        except socket.timeout:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error:
                pass
            tkMessageBox.showerror('Error','Waited too long for prefix')
            return
        if (len(input)!=20 or
            input[0]!='P'):
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except socket.error:
                pass
            tkMessageBox.showerror('Error','Invalid prefix information from LBR')
            return
        self.socket.settimeout(None) # no socket timeout from now on
        self.prefix = input[1:]
        # update GUI elements
        self.prefix = self.prefix
        self.status = 'connected to LBR@'+self.lbrAddr+':'+str(self.lbrPort)
        # release semaphore so task can start running
        self.varLock.acquire()
        self.isConnected = True
        self.varLock.release()
        self.connectSem.release()
    
    def disconnect(self):
        self.connectSem.acquire()
        # 
        self.varLock.acquire()
        self.isConnected = False
        self.varLock.release()
        # close the TCP session
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        # update GUI elements
        self.resetStats()
        self.connectButton.configure(text="Connect to LBR")
        self.connectButton.configure(command=self.connect)
    
    def send(self,lowpan):
        self.varLock.acquire()
        tempIsConnected = self.isConnected
        self.varLock.release()
        try:
            if tempIsConnected==True:
                self.socket.send(chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+lowpan)
                self.sentPackets += 1
                self.sentBytes   += len(lowpan)+8
            else:
                if self.sentColor=='red':
                    self.sentColor = 'orange'
                else:
                    self.sentColor = 'red'
        except socket.error:
            print 'ERROR: socket error while sending'
            pass