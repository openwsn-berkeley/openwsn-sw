import sys
import os
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(here, '..', '..'))                                # openvisualizer/
    sys.path.insert(0, os.path.join(here, '..', '..', '..', 'openUI'))                # openUI/

from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from networkState  import networkState
from lbrClient     import lbrClient
import OpenWindow
import OpenFrameState
import OpenFrameLbr

import Tkinter

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

class MenuUpdateFrame(Tkinter.Frame):
    
    def setMoteStateHandler(self,ms):
        self.ms              = ms
    
    def setMenuList(self,menuList):
        self.menuList        = menuList
    
    def updateMenuLabel(self,indexToUpdate):
        rawLabel  = self.ms.getStateElem(moteState.moteState.ST_IDMANAGER).get16bAddr()
        if rawLabel:
            menuLabel = ''.join(['%02x'%b for b in rawLabel])
            self.menuList.entryconfig(
                indexToUpdate,
                label=menuLabel,
            )
    
class MoteStateGui(object):
    
    GUI_UPDATE_PERIOD      = 500
    MENUENTRY_STATE        = 'mote state'
    MENUENTRY_LBRCLIENT    = 'lbrClient'
    
    def __init__(self,moteProbe_handlers,
                      moteConnector_handlers,
                      moteState_handlers,
                      lbrClient_handler,
                      lbrConnectParams_cb):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        self.moteConnector_handlers = moteConnector_handlers
        self.moteState_handlers     = moteState_handlers
        self.lbrClient_handler      = lbrClient_handler
        self.lbrConnectParams_cb    = lbrConnectParams_cb
        self.menuFrames             = []
        
        # local variables
        self.window                 = OpenWindow.OpenWindow("mote state GUI")
        
        #===== mote states frame
        menuNames                   = []
        self.menuFrames             = []
        for ms in self.moteState_handlers:
            thisFrame               = MenuUpdateFrame(self.window)
            thisFrame.setMoteStateHandler(ms)
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
                    moteState.moteState.ST_BACKOFF,
                ],
                [
                    moteState.moteState.ST_NEIGHBORS,
                    moteState.moteState.ST_QUEUE,
                ],
            ]
            for row in range(len(frameOrganization)):
                tempRowFrame = Tkinter.Frame(thisFrame)
                tempRowFrame.grid(row=row)
                for column in range(len(frameOrganization[row])):
                    stateType = frameOrganization[row][column]
                    tempFrameState = OpenFrameState.OpenFrameState(
                                guiParent=tempRowFrame,
                                frameName=stateType,
                                row=0,
                                column=column
                            )
                    tempFrameState.startAutoUpdate(
                                self.GUI_UPDATE_PERIOD,
                                ms.getStateElem,
                                (stateType,)
                            )
                    tempFrameState.show()
            
            menuNames       += ['{0}:{1}'.format(ms.moteConnector.moteProbeIp,ms.moteConnector.moteProbeTcpPort)]
            self.menuFrames += [thisFrame]
        
        # add to menu
        menuList = self.window.addMenuList(
            listname =  self.MENUENTRY_STATE,
            names =     menuNames,
            frames =    self.menuFrames,
        )
        
        for menuFrame in self.menuFrames:
            menuFrame.setMenuList(menuList)
        
        menuList.config(
            postcommand=self._updateMenuFrameNames
        )
        
        #===== network state
        
        # TODO
        
        #===== lbrClient frame
        
        thisFrame            = Tkinter.Frame(self.window)
        
        tempFrameLbrClient   = OpenFrameLbr.OpenFrameLbr(
            thisFrame,
            self.lbrClient_handler,
            self.lbrConnectParams_cb,
            row=1
        )
        tempFrameLbrClient.show()
        
        # add to menu
        self.window.addMenuItem(
            name =      self.MENUENTRY_LBRCLIENT,
            frame =     thisFrame,
        )
        
    #======================== public ==========================================
    
    def start(self):
        self.window.startGui()
    
    #======================== private =========================================
    
    def _updateMenuFrameNames(self):
        for i in range(len(self.menuFrames)):
            self.menuFrames[i].updateMenuLabel(i)
    
class MoteStateGui_app(object):
    
    def __init__(self):
        self.moteProbe_handlers        = []
        self.moteConnector_handlers    = []
        self.moteState_handlers        = []
        self.networkState_handler      = None
        self.lbrClient_handler         = None
        
        # create a moteProbe for each mote connected to this computer
        serialPorts    = moteProbe.utils.findSerialPorts()
        tcpPorts       = [TCP_PORT_START+i for i in range(len(serialPorts))]
        for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
            self.moteProbe_handlers.append(moteProbe.moteProbe(serialPort,tcpPort))
        
        # create a moteConnector for each moteProbe
        for mp in self.moteProbe_handlers:
           self.moteConnector_handlers.append(moteConnector.moteConnector(LOCAL_ADDRESS,mp.getTcpPort()))
        
        # create a moteState for each moteConnector
        for mc in self.moteConnector_handlers:
           self.moteState_handlers.append(moteState.moteState(mc))
        
        # create one networkState
        self.networkState_handler = networkState.networkState()
        
        # create one lbrClient
        self.lbrClient_handler    = lbrClient.lbrClient()
        
        # create an open GUI
        gui = MoteStateGui(self.moteProbe_handlers,
                           self.moteConnector_handlers,
                           self.moteState_handlers,
                           self.lbrClient_handler,
                           self.indicateConnectParams)
        
        # start threads
        self.lbrClient_handler.start()
        for ms in self.moteState_handlers:
           ms.start()
        for mc in self.moteConnector_handlers:
           mc.start()
        gui.start()
    
    #======================== GUI callbacks ===================================
    
    def indicateConnectParams(self,connectParams):
        try:
            self.lbrClient_handler.connect(
                connectParams['LBRADDR'],
                connectParams['LBRPORT'],
                connectParams['USERNAME']
            )
        except KeyError:
            log.error("malformed connectParams={0}".format(connectParams))
    
def main():
    app = MoteStateGui_app()
    
    
#============================ application logging =============================
import logging
import logging.handlers

#===== write everything to file

fileLogHandler = logging.handlers.RotatingFileHandler('moteStateGui.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
fileLogHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))

for loggerName in ['moteProbeUtils',
                   'moteProbe',
                   'moteConnector',
                   'OpenParser',
                   'Parser',
                   'ParserStatus',
                   'ParserInfoErrorCritical',
                   'ParserData',
                   'moteState',
                   'lbrClient',]:
    fileLogger = logging.getLogger(loggerName)
    fileLogger.setLevel(logging.ERROR)
    fileLogger.addHandler(fileLogHandler)
for loggerName in ['networkState',
                   'RPL']:
    fileLogger = logging.getLogger(loggerName)
    fileLogger.setLevel(logging.DEBUG)
    fileLogger.addHandler(fileLogHandler)
    

#===== print errors reported by motes on console

consoleLogHandler = logging.StreamHandler(sys.stdout)
consoleLogHandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s",datefmt='%H:%M:%S'))
    
for loggerName in ['ParserInfoErrorCritical',]:
    consoleLogger = logging.getLogger(loggerName)
    consoleLogger.setLevel(logging.INFO)
    consoleLogger.addHandler(consoleLogHandler)
    
if __name__=="__main__":
    main()