# Copyright (c) 2010-2013, Regents of the University of California.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  - Neither the name of the Regents of the University of California nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import sys
import os
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