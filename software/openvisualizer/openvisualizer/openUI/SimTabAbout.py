#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle
import SimTab

class SimTabAbout(SimTab.SimTab):
    
    def __init__(self,container):
        
        # store params
        
        # init parent
        SimTab.SimTab.__init__(self,container,'about')
        
        self.label = Tkinter.Label(self,text='poipoi about')
        self.label.grid(row=0,column=0)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    