import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbe')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

import moteProbeSerialThread
import moteProbeSocketThread
import utils

class moteProbe(object):
    
    def __init__(self,serialport,tcpport):
        
        # store params
        self.serialportName     = serialport[0]
        self.serialportBaudrate = serialport[1]
        self.tcpport            = tcpport
        
        # log
        log.info("creating moteProbe attaching to {0}@{1}, listening to TCP port {1}".format(
                    self.serialportName,
                    self.serialportBaudrate,
                    self.tcpport)
                )
        
        # local variables
        self.dataLock     = threading.Lock()
        
        # declare serial and socket threads
        self.serialThread = moteProbeSerialThread.moteProbeSerialThread(self.serialportName,self.serialportBaudrate)
        self.socketThread = moteProbeSocketThread.moteProbeSocketThread(self.tcpport)
        
        # inform one of another
        self.serialThread.setOtherThreadHandler(self.socketThread)
        self.socketThread.setOtherThreadHandler(self.serialThread)
        
        # start threads
        self.serialThread.start()
        self.socketThread.start()
    
    #======================== public ==========================================
    
    def getSerialPortName(self):
        self.dataLock.acquire()
        returnVal = self.serialportName
        self.dataLock.release()
        
        return returnVal
    
    def getSerialPortBaudrate(self):
        self.dataLock.acquire()
        returnVal = self.serialportBaudrate
        self.dataLock.release()
        
        return returnVal
    
    def getTcpPort(self):
        self.dataLock.acquire()
        returnVal = self.tcpport
        self.dataLock.release()
        
        return returnVal
        
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================