import sys
import os
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(here, '..', '..'))                                # openvisualizer/
    sys.path.insert(0, os.path.join(here, '..', '..', '..', 'openUI'))                # openUI/

from eventBus      import eventBusMonitor
from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from RPL           import RPL
from openTun       import openTun
import OpenWindow
import OpenFrameState
import OpenFrameLbr
import OpenFrameEventBus

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
    MENUENTRY_EVENTBUS     = 'eventBus'
    
    def __init__(self,eventBusMonitor,
                      moteProbes,
                      moteConnectors,
                      moteStates):
        
        # store params
        self.eventBusMonitor        = eventBusMonitor
        self.moteProbes             = moteProbes
        self.moteConnectors         = moteConnectors
        self.moteStates             = moteStates
        self.menuFrames             = []
        
        # local variables
        self.window                 = OpenWindow.OpenWindow("mote state GUI")
        
        #===== mote states frame
        menuNames                   = []
        self.menuFrames             = []
        for ms in self.moteStates:
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
        
        #===== eventBusMonitor Frame
        
        thisFrame            = Tkinter.Frame(self.window)
        
        tempFrameEventBus    = OpenFrameEventBus.OpenFrameEventBus(
            thisFrame,
            self.eventBusMonitor,
            row=1
        )
        tempFrameEventBus.show()
        
        # add to menu
        self.window.addMenuItem(
            name =      self.MENUENTRY_EVENTBUS,
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
        self.eventBusMonitor = None
        self.moteProbes      = []
        self.moteConnectors  = []
        self.moteStates      = []
        self.rpl             = None
        self.openTun         = None
        
        # create an eventBusMonitor
        self.eventBusMonitor = eventBusMonitor.eventBusMonitor()
        
        # create a moteProbe for each mote connected to this computer
        serialPorts          = moteProbe.utils.findSerialPorts()
        tcpPorts             = [TCP_PORT_START+i for i in range(len(serialPorts))]
        for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
            self.moteProbes.append(moteProbe.moteProbe(serialPort,tcpPort))
        
        # create a moteConnector for each moteProbe
        for mp in self.moteProbes:
           self.moteConnectors.append(moteConnector.moteConnector(LOCAL_ADDRESS,mp.getTcpPort()))
        
        # create a moteState for each moteConnector
        for mc in self.moteConnectors:
           self.moteStates.append(moteState.moteState(mc))
        
        # create a rpl instance
        self.rpl             = RPL.RPL()
        
        # create an openTun instance
        self.openTun         = openTun.OpenTun()
        
        # create an open GUI
        gui = MoteStateGui(
            self.eventBusMonitor,
            self.moteProbes,
            self.moteConnectors,
            self.moteStates,
        )
        
        # start threads
        for mc in self.moteConnectors:
           mc.start()
        gui.start()
    
    #======================== GUI callbacks ===================================
    
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
                   'eventBusMonitor',
                   'lbrClient',]:
    fileLogger = logging.getLogger(loggerName)
    fileLogger.setLevel(logging.ERROR)
    fileLogger.addHandler(fileLogHandler)
for loggerName in ['RPL',
                   'SourceRoute']:
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