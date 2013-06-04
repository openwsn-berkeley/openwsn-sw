import sys
import os
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(here, '..', '..'))                                # openvisualizer/
    sys.path.insert(0, os.path.join(here, '..', '..', '..', 'openUI'))                # openUI/

import logging
import logging.config

from optparse import OptionParser

from eventBus      import eventBusMonitor
from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from RPL           import RPL
from openLbr       import openLbr
from openTun       import openTun
from RPL           import UDPLatency
from RPL           import topology
import OpenWindow
import OpenFrameState
import OpenFrameButton
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
    MENUENTRY_STATE        = 'motes'
    MENUENTRY_LBR          = 'lbr'
    MENUENTRY_EVENTBUS     = 'eventBus'
    
    def __init__(self,eventBusMonitor,
                      moteProbes,
                      moteConnectors,
                      moteStates,
                      openLbr):
        
        # store params
        self.eventBusMonitor        = eventBusMonitor
        self.moteProbes             = moteProbes
        self.moteConnectors         = moteConnectors
        self.moteStates             = moteStates
        self.openLbr                = openLbr
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
                    moteState.moteState.ST_BACKOFF,
                ],
                [
                    moteState.moteState.TRIGGER_DAGROOT,
                    moteState.moteState.ST_IDMANAGER,
                ],
                [
                    moteState.moteState.ST_MACSTATS,
                ],
                [
                    moteState.moteState.ST_SCHEDULE,
                    moteState.moteState.ST_QUEUE,
                ],
                [
                    moteState.moteState.ST_NEIGHBORS,
                ],
            ]
            for row in range(len(frameOrganization)):
                tempRowFrame = Tkinter.Frame(thisFrame)
                tempRowFrame.grid(row=row)
                for column in range(len(frameOrganization[row])):
                    stateOrTrigger = frameOrganization[row][column]
                    if   stateOrTrigger in moteState.moteState.ST_ALL:
                        tempFrameState = OpenFrameState.OpenFrameState(
                            guiParent       = tempRowFrame,
                            frameName       = stateOrTrigger,
                            row             = 0,
                            column          = column,
                        )
                        tempFrameState.startAutoUpdate(
                            updatePeriod    = self.GUI_UPDATE_PERIOD,
                            updateFunc      = ms.getStateElem,
                            updateParams    = (stateOrTrigger,),
                        )
                        tempFrameState.show()
                    elif stateOrTrigger in moteState.moteState.TRIGGER_ALL:
                        tempFrameButton = OpenFrameButton.OpenFrameButton(
                            callfunction    = ms.triggerAction,
                            callparams      = (stateOrTrigger,),
                            guiParent       = tempRowFrame,
                            frameName       = stateOrTrigger,
                            buttonText      = 'toggle',
                            row             = 0,
                            column          = column,
                        )
                        tempFrameButton.show()
                    else:
                        raise SystemError('unexpected stateOrTrigger={0}'.format(stateOrTrigger))
            
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
        
        #===== openLbr Frame
        # TODO
        
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
    
    def __init__(self,simulatorMode):
        
        # store params
        self.simulatorMode   = simulatorMode
        print self.simulatorMode
        # local variables
        self.eventBusMonitor = None
        self.moteProbes      = []
        self.moteConnectors  = []
        self.moteStates      = []
        self.rpl             = None
        self.openLbr         = None
        self.openTun         = None
        self.udpLatency      = None
        self.topology        = None
        
        # create an eventBusMonitor
        self.eventBusMonitor = eventBusMonitor.eventBusMonitor()
        
        # create a moteProbe for each mote connected to this computer
        serialPorts          = moteProbe.utils.findSerialPorts()
        tcpPorts             = [TCP_PORT_START+i for i in range(len(serialPorts))]
        for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
            self.moteProbes.append(moteProbe.moteProbe(serialPort,tcpPort))
        
        # create a moteConnector for each moteProbe
        for mp in self.moteProbes:
           self.moteConnectors.append(moteConnector.moteConnector(LOCAL_ADDRESS,mp.getTcpPort(),mp.getSerialPortName()))
        
        # create a moteState for each moteConnector
        for mc in self.moteConnectors:
           self.moteStates.append(moteState.moteState(mc))
        
        self.topology        = topology.topology()
        
        # create a rpl instance
        self.rpl             = RPL.RPL()
        
        # create an openLbr instance
        self.openLbr         = openLbr.OpenLbr()
        
        # create an openTun instance
        self.openTun         = openTun.OpenTun()
        
        self.udpLatency      = UDPLatency.UDPLatency()
        # create an open GUI
        gui = MoteStateGui(
            self.eventBusMonitor,
            self.moteProbes,
            self.moteConnectors,
            self.moteStates,
            self.openLbr,
        )
        
        gui.start()
    
    #======================== GUI callbacks ===================================

#============================ main ============================================

def parseCliOptions():
    
    parser = OptionParser()
    
    parser.add_option( '--sim', '-s',
        dest       = 'simulatorMode',
        default    = False,
        action     = 'store_true',
    )
    
    (opts, args)  = parser.parse_args()
    
    return opts

def main(simulatorMode):
    appDir = '.'
    logging.config.fileConfig(os.path.join(appDir,'logging.conf'), {'logDir': appDir})
    app = MoteStateGui_app(simulatorMode)

if __name__=="__main__":
    
    opts = parseCliOptions()
    
    main(simulatorMode=opts.__dict__['simulatorMode'])