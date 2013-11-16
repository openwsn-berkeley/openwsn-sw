#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle
import SimFrame

class SimTab(SimFrame.SimFrame):
    
    def __init__(self,container,name):
        
        # store params
        self.name = name
        
        # init parent
        Tkinter.Frame.__init__(self,master=container,
                                    relief=Tkinter.SUNKEN,
                                    borderwidth=1,
                                    bg=SimStyle.COLOR_BG,
                                    width=SimStyle.WIDTH_CONTAINER,
                                    height=SimStyle.HEIGHT_CONTAINER)
    
    #======================== public ==========================================
    
    def getName(self):
        return self.name
    
    #======================== private =========================================
    