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
        self.serialport = serialport
        self.tcpport    = tcpport
        
        # log
        log.info("creating moteProbe attaching to {0}, listening to TCP port {1}".format(
                    self.serialport,
                    self.tcpport)
                )
        
        # declare serial and socket threads
        self.serialThread = moteProbeSerialThread.moteProbeSerialThread(self.serialport)
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