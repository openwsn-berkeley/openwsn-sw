import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbeSerialThread')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import serial

from EventBus import EventBus

class moteProbeSerialThread(threading.Thread):

    def __init__(self,serialportName,serialportBaudrate):
        
        # log
        log.debug("create instance")
        
        # store params
        self.serialportName       = serialportName
        self.serialportBaudrate   = serialportBaudrate
        
        # local variables
        self.serialInput          = ''
        self.serialOutput         = ''
        self.serialOutputLock     = threading.Lock()
        self.state                = 'WAIT_HEADER'
        self.numdelimiter         = 0
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'moteProbeSerialThread@'+self.serialportName
        
        # subscribe to eventBus
        EventBus.EventBus().subscribe(
            self.send,
            'moteProbe.{0}.bytesFromTcpPort'.format(self.serialportName),
        )
    
    def run(self):
        
        # log
        log.debug("start running")
    
        while True:     # open serial port
            log.debug("open serial port")
            self.serial = serial.Serial(self.serialportName,self.serialportBaudrate)
            while True: # read bytes from serial port
                try:
                    char = self.serial.read(1)
                except Exception as err:
                    log.warning(err)
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
                                # publish copy of serial input on eventBus (synchronously)
                                EventBus.EventBus().publish_sync(
                                    'moteProbe.{0}.bytesFromSerialPort'.format(self.serialportName),
                                    self.serialInput[:],
                                    minNumReceivers=1,
                                    maxNumReceivers=1,
                                )
                    else:
                        raise SystemError("invalid state {0}".format(state))
    
    #======================== public ==========================================
    
    def send(self,bytesToSend):
        self.serialOutputLock.acquire()
        if len(self.serialOutput)>255:
            log.error("serialOutput overflow ({0} bytes)".format(len(self.serialOutput)))
        
        self.serialOutput += bytesToSend[0]+ chr(len(self.serialOutput)) + bytesToSend[1:]
        if len(self.serialOutput)>200:
            log.warning("serialOutput overflowing ({0} bytes)".format(len(self.serialOutput)))
        self.serialOutputLock.release()
    
    #======================== private =========================================