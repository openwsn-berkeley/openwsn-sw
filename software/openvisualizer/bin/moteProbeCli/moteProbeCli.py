import os
import sys
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openCli'))    # openCli/
    sys.path.insert(0, os.path.join(cur_path, '..', '..','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/

from moteProbe     import moteProbe
from OpenCli       import OpenCli

TCP_PORT_START = 8090

class moteProbeCli(OpenCli):

    def __init__(self,moteProbe_handlers):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        
        # initialize parent class
        OpenCli.__init__(self,"mote probe CLI",self.quit_cb)
         
        # add commands
        self.registerCommand('status',
                             's',
                             'print status',
                             [],
                             self._handlerStatus)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def _handlerStatus(self,params):
        output = []
        
        for mp in self.moteProbe_handlers:
            output += [' - serial port {0}@{1} presented on TCP port {2}'.format(
                            mp.getPortName(),
                            mp.getSerialPortBaudrate(),
                            mp.getTcpPort())]
        
        print '\n'.join(output)
    
    #===== helpers
    
    def quit_cb(self):
        for mb in self.moteProbe_handlers:
           mb.quit()

def main():
    
    moteProbe_handlers = []

    # create a moteProbe for each mote connected to this computer
    serialPortNames     = moteProbe.utils.findSerialPorts()
    port_numbers        = [TCP_PORT_START+i for i in range(len(serialPortNames))]
    for (serialPortName,port_number) in zip(serialPortNames,port_numbers):
        moteProbe_handlers.append(moteProbe.moteProbe(serialPortName,port_number))

    # create an open CLI
    cli = moteProbeCli(moteProbe_handlers)
    cli.start()

#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('moteProbe.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['moteProbe']:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()