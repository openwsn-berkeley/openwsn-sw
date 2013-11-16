#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle

class SimFrame(Tkinter.Frame):
    
    def __init__(self):
        
        # init parent
        Tkinter.Frame.__init__(self,relief=Tkinter.SUNKEN,
                                    borderwidth=1,
                                    bg=SimStyle.COLOR_BG)
    
    #======================== public ==========================================
    
    #======================== private =========================================