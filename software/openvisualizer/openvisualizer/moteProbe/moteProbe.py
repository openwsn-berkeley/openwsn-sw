# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('moteProbe')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import os
if os.name=='nt':       # Windows
   import _winreg as winreg
elif os.name=='posix':  # Linux
   import glob
import threading

import serial
import time
import sys

from   pydispatch import dispatcher
import OpenHdlc
import openvisualizer.openvisualizer_utils as u
from   openvisualizer.moteConnector import OpenParser

#============================ functions =======================================

BAUDRATE_TELOSB = 115200
BAUDRATE_GINA   = 115200
BAUDRATE_WSN430 = 115200

def findSerialPorts():
    '''
    Returns the serial ports of the motes connected to the computer.
    
    :returns: A list of tuples (name,baudrate) where:
        - name is a strings representing a serial port, e.g. 'COM1'
        - baudrate is an int representing the baurate, e.g. 115200
    '''
    serialports = []
    
    if os.name=='nt':
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        for i in range(winreg.QueryInfoKey(key)[1]):
            try:
                val = winreg.EnumValue(key,i)
            except:
                pass
            else:
                if   val[0].find('VCP')>-1:
                    serialports.append( (str(val[1]),BAUDRATE_TELOSB) )
                elif val[0].find('Silabser')>-1:
                    serialports.append( (str(val[1]),BAUDRATE_GINA) )
                elif val[0].find('ProlificSerial')>-1:
                    serialports.append( (str(val[1]),BAUDRATE_WSN430) )
    elif os.name=='posix':
        serialports = [(s,BAUDRATE_GINA) for s in glob.glob('/dev/ttyUSB*')]
    
    # log
    log.info("discovered following COM port: {0}".format(['{0}@{1}'.format(s[0],s[1]) for s in serialports]))
    
    return serialports

#============================ class ===========================================

class moteProbe(threading.Thread):
    
    def __init__(self,serialport=None,emulatedMote=None):
        assert bool(serialport) != bool(emulatedMote)
        
        if serialport:
            assert not emulatedMote
            self.realserial       = True
        else:
            assert not serialport
            self.realserial       = False
        
        # store params
        if self.realserial:
            # import pyserial module (needs to be installed)
            import serial
            
            # store params
            self.serialport       = serialport[0]
            self.baudrate         = serialport[1]
            
            # log
            log.info("creating moteProbe attaching to serialport {0}@{1}".format(
                    self.serialport,
                    self.baudrate,
                )
            )
        else:
            # store params
            self.emulatedMote     = emulatedMote
            self.serialport       = 'emulated{0}'.format(self.emulatedMote.getId())
            
            # log
            log.info("creating moteProbe attaching to emulated mote {0}".format(
                    self.serialport,
                )
            )
        
        # local variables
        self.hdlc                 = OpenHdlc.OpenHdlc()
        self.lastRxByte           = self.hdlc.HDLC_FLAG
        self.busyReceiving        = False
        self.inputBuf             = ''
        self.outputBuf            = []
        self.outputBufLock        = threading.RLock()
        self.dataLock             = threading.Lock()
        # flag to permit exit from read loop
        self.goOn                 = True
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'moteProbe@'+self.serialport
        
        if not self.realserial:
            # Non-daemonized moteProbe does not consistently die on close(),
            # so ensure moteProbe does not persist.
            self.daemon           = True
        
        # connect to dispatcher
        dispatcher.connect(
            self._bufferDataToSend,
            signal = 'fromMoteConnector@'+self.serialport,
        )
    
        # start myself
        self.start()
    
    #======================== thread ==========================================
    
    def run(self):
        try:
            # log
            log.info("start running")
        
            while self.goOn:     # open serial port
                if self.realserial:
                    log.info("open serial port {0}@{1}".format(self.serialport,self.baudrate))
                    self.serial = serial.Serial(self.serialport,self.baudrate)
                else:
                    log.info("use emulated serial port {0}".format(self.serialport))
                    self.serial = self.emulatedMote.bspUart
                while self.goOn: # read bytes from serial port
                    try:
                        if self.realserial:
                            rxBytes = self.serial.read(1)
                        else:
                            rxBytes = self.serial.read()
                    except Exception as err:
                        print err
                        log.warning(err)
                        time.sleep(1)
                        break
                    else:
                        for rxByte in rxBytes:
                            if      (
                                        (not self.busyReceiving)             and 
                                        self.lastRxByte==self.hdlc.HDLC_FLAG and
                                        rxByte!=self.hdlc.HDLC_FLAG
                                    ):
                                # start of frame
                                if log.isEnabledFor(logging.DEBUG):
                                    log.debug("{0}: start of hdlc frame {1} {2}".format(self.name, u.formatStringBuf(self.hdlc.HDLC_FLAG), u.formatStringBuf(rxByte)))
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
                                if log.isEnabledFor(logging.DEBUG):
                                    log.debug("{0}: end of hdlc frame {1} ".format(self.name, u.formatStringBuf(rxByte)))
                                self.busyReceiving       = False
                                self.inputBuf           += rxByte
                                
                                try:
                                    tempBuf = self.inputBuf
                                    self.inputBuf        = self.hdlc.dehdlcify(self.inputBuf)
                                    if log.isEnabledFor(logging.DEBUG):
                                        log.debug("{0}: {2} dehdlcized input: {1}".format(self.name, u.formatStringBuf(self.inputBuf), u.formatStringBuf(tempBuf)))
                                except OpenHdlc.HdlcException as err:
                                    log.warning('{0}: invalid serial frame: {2} {1}'.format(self.name, err, u.formatStringBuf(tempBuf)))
                                else:
                                    if self.inputBuf==chr(OpenParser.OpenParser.SERFRAME_MOTE2PC_REQUEST):
                                        with self.outputBufLock:
                                            if self.outputBuf:
                                                outputToWrite = self.outputBuf.pop(0)
                                                self.serial.write(outputToWrite)
                                    else:
                                        # dispatch
                                        dispatcher.send(
                                            sender        = self.name,
                                            signal        = 'fromMoteProbe@'+self.serialport,
                                            data          = [ord(c) for c in self.inputBuf],
                                        )
                            
                            self.lastRxByte = rxByte
                        
                    if not self.realserial:
                        rxByte = self.serial.doneReading()
        except Exception as err:
            errMsg=u.formatCrashMessage(self.name,err)
            print errMsg
            log.critical(errMsg)
            sys.exit(-1)
    
    #======================== public ==========================================
    
    def getSerialPortName(self):
        with self.dataLock:
            return self.serialport
    
    def getSerialPortBaudrate(self):
        with self.dataLock:
            return self.baudrate
    
    def close(self):
        self.goOn = False
    
    #======================== private =========================================
    
    def _bufferDataToSend(self,data):
        
        # frame with HDLC
        hdlcData = self.hdlc.hdlcify(data)
        
        # add to outputBuf
        with self.outputBufLock:
            self.outputBuf += [hdlcData]
