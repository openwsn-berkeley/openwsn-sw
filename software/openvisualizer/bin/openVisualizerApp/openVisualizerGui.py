# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below, 
# where both the copyright owner and organization are the Regents of the  
# University of California. 
# https://openwsn.atlassian.net/wiki/display/OW/License

import sys
import os

import pathHelper
if __name__=="__main__":
    pathHelper.updatePath()

import logging
log = logging.getLogger('openVisualizerGui')

from moteState     import moteState

import openVisualizerApp
import OpenWindow
import OpenFrameState
import OpenFrameButton
import OpenFrameEventBus
import openvisualizer_utils as u

import Tkinter

class MenuUpdateFrame(Tkinter.Frame):
    """Updates the motes menu items with mote 16-bit IDs"""
    
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

class OpenVisualizerGui(object):
    
    GUI_UPDATE_PERIOD      = 500
    MENUENTRY_STATE        = 'motes'
    MENUENTRY_LBR          = 'lbr'
    MENUENTRY_EVENTBUS     = 'eventBus'
    
    def __init__(self,app):
        """Sets menu names initially to serial port ID"""
        log.info('Creating OpenVisualizerGui')
        
        # store params
        self.app                    = app
        
        # local variables
        self.window                 = OpenWindow.OpenWindow("OpenVisualizer", self)
        
        #===== mote states frame
        menuNames                   = []
        self.menuFrames             = []
        for ms in self.app.moteStates:
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
            
            menuNames       += ['{0}'.format(ms.moteConnector.serialport)]
            self.menuFrames += [thisFrame]
        
        # Add to menu; returns Tkinter.Menu
        menuList = self.window.addMenuList(
            listname =  self.MENUENTRY_STATE,
            names =     menuNames,
            frames =    self.menuFrames,
        )
        
        for menuFrame in self.menuFrames:
            menuFrame.setMenuList(menuList)
        
        menuList.config(
            # Executes when menu displayed.
            postcommand=self._updateMenuFrameNames
        )
        
        #===== openLbr Frame
        # TODO
        
        #===== eventBusMonitor Frame
        
        thisFrame            = Tkinter.Frame(self.window)
        
        tempFrameEventBus    = OpenFrameEventBus.OpenFrameEventBus(
            thisFrame,
            self.app.eventBusMonitor,
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
        
    def close(self):
        self.app.close()
    
    #======================== private =========================================
    
    def _updateMenuFrameNames(self):
        for i in range(len(self.menuFrames)):
            self.menuFrames[i].updateMenuLabel(i)


#============================ main ============================================

if __name__=="__main__":
    app = openVisualizerApp.main()
    gui = OpenVisualizerGui(app)
    gui.start()