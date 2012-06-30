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
        
    def quit(self):
        raise NotImplementedError()
    
    #======================== private =========================================

'''
if this module is run by itself (i.e. not imported from OpenVisualizer),
it has to create moteProbe threads for each mote connected
'''
if __name__ == '__main__':
    
    import os
    import sys
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..', 'openCli'))      # openCli/
    
    import       logging.handlers
    from OpenCli import OpenCli
    
    class moteProbeCli(OpenCli):
    
        def __init__(self,moteProbe_handlers):
            
            # store params
            self.moteProbe_handlers     = moteProbe_handlers
            
            # initialize parent class
            OpenCli.__init__(self,"mote probe CLI",self.quit_cb)
        
        def quit_cb(self):
            
            for mb in self.moteProbe_handlers:
               mb.quit()
    
    # logging
    logHandler = logging.handlers.RotatingFileHandler('moteProbe.log',
                                                      maxBytes=2000000,
                                                      backupCount=5,
                                                      mode='w')
    logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
    for loggerName in ['moteProbe',
                       'moteProbeSerialThread',
                       'moteProbeSocketThread',
                       'moteProbeUtils']:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(logHandler)
    
    moteProbe_handlers = []
    
    # create and start mote probe instances
    serialPortNames     = utils.findSerialPorts()
    port_numbers        = [8080+i for i in range(len(serialPortNames))]
    for (serialPortName,port_number) in zip(serialPortNames,port_numbers):
        moteProbe_handlers.append(moteProbe(serialPortName,port_number))
    
    # cli
    cli = moteProbeCli(moteProbe_handlers)
    cli.start()