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
        self.hdlc                 = openhdlc.OpenHdlc()
        self.lastRxByte           = self.hdlc.HDLC_FLAG
        self.busyReceiving        = False
        self.inputBuf             = ''
        self.outputBuf            = []
        self.outputBufLock        = threading.RLock()
        
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
                    rxByte = self.serial.read(1)
                except Exception as err:
                    log.warning(err)
                    time.sleep(1)
                    break
                else:
                    #log.debug("received {0} ({1})".format(rxByte,hex(ord(rxByte))))
                    if      (
                                (not self.busyReceiving)             and 
                                self.lastRxByte==self.hdlc.HDLC_FLAG and
                                rxByte!=self.hdlc.HDLC_FLAG
                            ):
                        # start of frame
                        
                        self.busyReceiving       = True
                        self.inputBuf            = self.hdlc.HDLC_FLAG
                        self.inputBuf           += rxByte
                    elif    (
                                self.busyReceiving                   and
                                rxByte!=self.hdlc.HDLC_FLAG
                            ):
                        # middle of frame
                        
                        self.inputBuf           += rxByte
                    elif    (
                                self.busyReceiving                   and
                                rxByte==self.hdlc.HDLC_FLAG
                            ):
                        # end of frame
                        
                        self.busyReceiving       = False
                        self.inputBuf           += rxByte
                        
                        try:
                            self.inputBuf        = self.hdlc.dehdlcify(self.inputBuf)
                        except openhdlc.HdlcException:
                            print "wrong CRC!"
                        else:
                            if self.inputBuf==chr(OpenParser.OpenParser.SERFRAME_MOTE2PC_REQUEST):
                                with self.outputBufLock:
                                    if self.outputBuf:
                                        outputToWrite = self.outputBuf.pop(0)
                                        self.serial.write(outputToWrite)
                                        log.debug('sent {0} bytes over serial:   {1}'.format(
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
                    
                    self.lastRxByte = rxByte
    
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