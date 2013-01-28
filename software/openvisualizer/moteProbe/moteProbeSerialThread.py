import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbeSerialThread')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import serial
import time
import struct

import openhdlc
from moteConnector import OpenParser
import openvisualizer_utils as u

from pydispatch import dispatcher

class moteProbeSerialThread(threading.Thread):

    def __init__(self,serialportName,serialportBaudrate):
        
        # log
        log.debug("create instance")
        
        # store params
        self.serialportName       = serialportName
        self.serialportBaudrate   = serialportBaudrate
        
        # local variables
        self.inputBuf             = ''
        self.outputBuf            = []
        self.outputBufLock        = threading.RLock()
        self.state                = 'WAIT_HEADER'
        self.numdelimiter         = 0
        self.hdlc                 = openhdlc.OpenHdlc()
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'moteProbeSerialThread@'+self.serialportName
        
        # connect to dispatcher
        dispatcher.connect(
            self.send,
            signal = 'bytesFromTcpPort'+self.serialportName,
        )
    
    def run(self):
        
        # log
        log.debug("start running")
    
        while True:     # open serial port
            log.debug("open serial port {0}@{1}".format(self.serialportName,self.serialportBaudrate))
            self.serial = serial.Serial(self.serialportName,self.serialportBaudrate)
            while True: # read bytes from serial port
                try:
                    char = self.serial.read(1)
                except Exception as err:
                    log.warning(err)
                    time.sleep(1)
                    break
                else:
                    #log.debug("received {0} ({1})".format(char,hex(ord(char))))
                    if    self.state == 'WAIT_HEADER':
                        if char==self.hdlc.HDLC_FLAG:
                            self.numdelimiter     += 1
                        else:
                            self.numdelimiter      = 0
                        if self.numdelimiter==1:
                            self.state             = 'RECEIVING_COMMAND'
                            self.inputBuf          = char
                            self.numdelimiter      = 0
                    elif self.state == 'RECEIVING_COMMAND':
                        self.inputBuf = self.inputBuf+char
                        if char==self.hdlc.HDLC_FLAG:
                            self.numdelimiter     += 1
                        else:
                            self.numdelimiter      = 0
                        if self.numdelimiter==1:
                            self.state             = 'WAIT_HEADER'
                            self.numdelimiter      = 0
                            try:
                                self.inputBuf   = self.hdlc.dehdlcify(self.inputBuf)
                            except openhdlc.HdlcException:
                                print "wrong CRC!"
                            if self.inputBuf==chr(OpenParser.OpenParser.SERFRAME_MOTE2PC_REQUEST):
                                with self.outputBufLock:
                                    if self.outputBuf:
                                        outputToWrite = self.outputBuf.pop(0)
                                        self.serial.write(outputToWrite)
                                        log.debug('sent {0} bytes over serial: {1}'.format(
                                                len(outputToWrite),
                                                u.formatBuf(outputToWrite),
                                            )
                                        )
                            else:
                                # dispatch
                                dispatcher.send(
                                    signal        = 'bytesFromSerialPort'+self.serialportName,
                                    data          = self.inputBuf[:],
                                )
                    else:
                        raise SystemError("invalid state {0}".format(state))
    
    #======================== public ==========================================
    
    def send(self,data):
        # frame with HDLC
        hdlcData = self.hdlc.hdlcify(data)
        
        # add to outputBuf
        with self.outputBufLock:
            self.outputBuf += [hdlcData]
        
        # log
        log.debug('added {0} bytes to outputBuf: {1}'.format(
                len(hdlcData),
                u.formatBuf(hdlcData),
            )
        )
    
    #======================== private =========================================