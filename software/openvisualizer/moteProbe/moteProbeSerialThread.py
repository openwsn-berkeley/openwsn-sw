import threading
import serial

class moteProbeSerialThread(threading.Thread):

    def __init__(self,serialport):
        
        # store params
        self.serialport           = serialport
        
        # local variables
        self.serialInput          = ''
        self.serialOutput         = ''
        self.serialOutputLock     = threading.Lock()
        self.state                = 'WAIT_HEADER'
        self.numdelimiter         = 0
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'moteProbeSerialThread@'+self.serialport
    
    def run(self):
        while True:    # open serial port
            self.serial = serial.Serial(self.serialport,baudrate=115200)
            while True: # read bytes from serial port
                try:
                    char = self.serial.read(1)
                except:
                    err = sys.exc_info()
                    sys.stderr.write( "ERROR moteProbeSerialThread: %s (%s) \n" % (str(err[0]), str(err[1])))
                    time.sleep(1)
                    break
                else:
                    if    self.state == 'WAIT_HEADER':
                        if char == '^':
                            self.numdelimiter     += 1
                        else:
                            self.numdelimiter      = 0
                        if self.numdelimiter==3:
                            self.state             = 'RECEIVING_COMMAND'
                            self.serialInput       = ''
                            self.numdelimiter      = 0
                    elif self.state == 'RECEIVING_COMMAND':
                        self.serialInput = self.serialInput+char
                        if char == '$':
                            self.numdelimiter     += 1
                        else:
                            self.numdelimiter      = 0
                        if self.numdelimiter==3:
                            self.state             = 'WAIT_HEADER'
                            self.numdelimiter      = 0
                            self.serialInput       = self.serialInput.rstrip('$')
                            #byte 0 is the type of status message
                            if self.serialInput[0]=="R":     #request for data
                                if (ord(self.serialInput[1])==200):  # byte 1 indicates free space in mote's input buffer
                                    self.serialOutputLock.acquire()
                                    self.serial.write(self.serialOutput)
                                    self.serialOutput = ''
                                    self.serialOutputLock.release()
                            else:
                                # send to other thread
                                self.otherThreadHandler.send(self.serialInput)
                    else:
                        print 'ERROR [moteProbeSerialThread]: invalid state='+state
    
    #======================== public ==========================================
    
    def setOtherThreadHandler(self,otherThreadHandler):
        self.otherThreadHandler = otherThreadHandler
    
    def send(self,bytesToSend):
        self.serialOutputLock.acquire()
        self.serialOutput += 'D'+ chr(len(self.serialOutput)) + bytesToSend
        if len(self.serialOutput)>200:
            print 'WARNING [moteProbeSerialThread@'+self.serialport+'] serialOutput overflowing ('+str(len(self.serialOutput))+' bytes)'
        self.serialOutputLock.release()
    
    #======================== private =========================================