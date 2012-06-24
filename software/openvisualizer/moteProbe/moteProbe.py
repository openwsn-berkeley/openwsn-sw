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
        
        # log
        log.debug("create instance")
        
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
    
    #======================== private =========================================

'''
if this module is run by itself (i.e. not imported from OpenVisualizer),
it has to create moteProbe threads for each mote connected
'''
if __name__ == '__main__':
    
    import logging.handlers
    
    # logging
    logHandler = logging.handlers.RotatingFileHandler('moteProbe.log',
                                                   maxBytes=2000000,
                                                   backupCount=5,
                                                   mode='w'
                                                   )
    logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
    for loggerName in ['moteProbe',
                       'moteProbeSerialThread',
                       'moteProbeSocketThread',
                       'moteProbeUtils']:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(logHandler)
    
    # banner
    banner = 'moteProbe - Open WSN project'
    print banner
    log.info(banner)
    
    # create and start mote probe instances
    serialPortNames     = utils.findSerialPortsNames()
    port_numbers        = [8080+i for i in range(len(serialPortNames))]
    for (serialPortName,port_number) in zip(serialPortNames,port_numbers):
        moteProbe(serialPortName,port_number)
