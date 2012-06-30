import sys
import os
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..')) # openvisualizer/

from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

def main():
    
    moteProbe_handlers     = []
    moteConnector_handlers = []
    moteState_handlers     = []
    
    # create a moteProbe for each mote connected to this computer
    serialPorts    = moteProbe.utils.findSerialPorts()
    tcpPorts       = [TCP_PORT_START+i for i in range(len(serialPorts))]
    for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
        moteProbe_handlers.append(moteProbe.moteProbe(serialPort,tcpPort))
    
    # create a moteConnector for each moteProbe
    for mp in moteProbe_handlers:
       moteConnector_handlers.append(moteConnector.moteConnector(LOCAL_ADDRESS,mp.getTcpPort()))
    
    # create a moteState for each moteConnector
    for mc in moteConnector_handlers:
       moteState_handlers.append(moteState.moteState(mc))
    
    # start threads
    for mc in moteConnector_handlers:
       mc.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('openVisualizer.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['moteProbe',
                   'moteConnector',
                   'OpenParser',
                   'Parser',
                   'ParserStatus',
                   'moteState',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()