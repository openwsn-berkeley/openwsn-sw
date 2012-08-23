import moteProbeSerialThread
import moteProbeSocketThread
import utils

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbe')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

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
    
    def getTcpPort(self):
        return self.tcpport
        
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================