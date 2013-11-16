#!/usr/bin/python

import sys
import Tkinter
from SimStyle import SimStyle
import sim_version

class SimWindow(Tkinter.Tk):
    
    def __init__(self):
        
        # init parent
        Tkinter.Tk.__init__(self)
        
        # name of the windowign
        self.title('OpenWSN Simulator')
        
        # call releaseAndQuit when the close button is pressed
        self.protocol('WM_DELETE_WINDOW',self._releaseAndQuit)
        
        # status bar with version
        versionString = '.'.join([str(i) for i in sim_version.VERSION])
        temp = Tkinter.Label(self,
                             font=SimStyle.FONT_BODY,
                             text="OpenSim "+versionString,
                             anchor=Tkinter.E)
        temp.grid(row=100,column=0,sticky=Tkinter.W+Tkinter.E)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _releaseAndQuit(self):
        
        # close the GUI
        self.quit()
        
        # exit
        sys.exit() 