import sys
import os
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openCli'))    # openCli/
    
from moteProbe     import moteProbe
from moteConnector.SerialEchoMoteConnector import SerialEchoMoteConnector
from moteState     import moteState
from OpenCli       import OpenCli

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090
MAX_BYTES_TO_SEND = 50

class serialEchoCli(OpenCli):
    
    def __init__(self,moteProbe_handlers,moteConnector_handlers,moteState_handlers):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        self.moteConnector_handlers = moteConnector_handlers
        self.moteState_handlers     = moteState_handlers
    
        # initialize parent class
        OpenCli.__init__(self,"serial Echo Cli",self._quit_cb)
        
        # add commands
        self.registerCommand('testserial',
                             't',
                             'test serial port',
                             [],
                             self._handlerTestSerial)
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def _handlerTestSerial(self,params):
        data="";
        for i in range(MAX_BYTES_TO_SEND):
            data+=str(i)
            
        self.moteConnector_handlers[0].write(data)
    
    
    #===== helpers
    
    def _quit_cb(self):
        
        for mc in self.moteConnector_handlers:
           mc.quit()
        for mb in self.moteProbe_handlers:
           mb.quit()

def main():
    
    moteProbe_handlers     = []
    moteConnector_handlers = []
    moteState_handlers     = []
    
    # create a moteProbe for each mote connected to this computer
    serialPorts    = moteProbe.utils.findSerialPorts()
    tcpPorts       = [TCP_PORT_START+i for i in range(len(serialPorts))]
    
    #picking the first available
    moteProbe_handlers.append(moteProbe.moteProbe(serialPorts[0],tcpPorts[0]))
    
    # create a moteConnector for each moteProbe
    for mp in moteProbe_handlers:
       moteConnector_handlers.append(SerialEchoMoteConnector(LOCAL_ADDRESS,mp.getTcpPort()))
    
    # create a moteState for each moteConnector
    for mc in moteConnector_handlers:
       moteState_handlers.append(moteState.moteState(mc))
    
    # create an open CLI
    cli = serialEchoCli(moteProbe_handlers,
                       moteConnector_handlers,
                       moteState_handlers)
    
    # start threads
    for ms in moteState_handlers:
       ms.start()
    for mc in moteConnector_handlers:
       mc.start()
    cli.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('serialEchoCli.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in [
                   'SerialEchoMoteConnector',
                   'OpenCli',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()