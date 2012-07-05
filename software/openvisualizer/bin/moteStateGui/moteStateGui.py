import sys
import os
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openUI'))     # openUI/

from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
import OpenWindow
import OpenFrameState

import Tkinter

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

class MoteStateGui(object):
    
    GUI_UPDATE_PERIOD = 500
    
    def __init__(self,moteProbe_handlers,moteConnector_handlers,moteState_handlers):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        self.moteConnector_handlers = moteConnector_handlers
        self.moteState_handlers     = moteState_handlers
        
        # local variables
        self.stateFrames            = {}
        
        self.window     = OpenWindow.OpenWindow("mote state GUI")
        
        frameOrganization = [
            [
                moteState.moteState.ST_ISSYNC,
                moteState.moteState.ST_ASN,
                moteState.moteState.ST_MYDAGRANK,
                moteState.moteState.ST_OUPUTBUFFER,
            ],
            [
                moteState.moteState.ST_IDMANAGER,
                moteState.moteState.ST_MACSTATS,
            ],
            [
                moteState.moteState.ST_SCHEDULE,
            ],
            [
                moteState.moteState.ST_NEIGHBORS,
                moteState.moteState.ST_QUEUE,
            ],
        ]
        
        for row in range(len(frameOrganization)):
            tempRowFrame = Tkinter.Frame(self.window)
            tempRowFrame.grid(row=row)
            for column in range(len(frameOrganization[row])):
                stateType = frameOrganization[row][column]
                self.stateFrames[stateType]   = OpenFrameState.OpenFrameState(
                                                    tempRowFrame,
                                                    frameName=stateType,
                                                    row=0,
                                                    column=column
                                                )
                self.stateFrames[stateType].startAutoUpdate(
                                                    self.GUI_UPDATE_PERIOD,
                                                    self.moteState_handlers[0].getStateElem,
                                                    (stateType,)
                                                )
                self.stateFrames[stateType].show()
    
    #======================== public ==========================================
    
    def start(self):
        self.window.startGui()
    
    #======================== private =========================================

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
    
    # create an open GUI
    gui = MoteStateGui(moteProbe_handlers,
                       moteConnector_handlers,
                       moteState_handlers)
    
    # start threads
    for ms in moteState_handlers:
       ms.start()
    for mc in moteConnector_handlers:
       mc.start()
    gui.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('moteStateGui.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['moteProbe',
                   'moteConnector',
                   'OpenParser',
                   'Parser',
                   'ParserStatus',
                   'ParserError',
                   'ParserData',
                   'moteState',
                   'OpenCli',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()