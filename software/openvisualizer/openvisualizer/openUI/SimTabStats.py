#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle
import SimTab

class SimTabStats(SimTab.SimTab):
    
    UPDATEPERIOD = 1000
    
    def __init__(self,container,engine):
        
        # init parent
        SimTab.SimTab.__init__(self,container,'stats')
        
        # store params
        self.engine   = engine
        
        self.durationRunning = Tkinter.Label(self)
        self.durationRunning.grid(row=0,column=0)
        
        self.numEvents = Tkinter.Label(self)
        self.numEvents.grid(row=1,column=0)
        
        self.after(self.UPDATEPERIOD,self._updateGui)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _updateGui(self):
        
        temp = 'durationRunning = {0:.0f}s'.format(self.engine.getStats().getDurationRunning())
        self.durationRunning.configure(text=temp)
        temp = 'numEvents = {0}'.format(self.engine.timeline.getStats().getNumEvents())
        self.numEvents.configure(text=temp)
        
        # reschedule next update
        self.after(self.UPDATEPERIOD,self._updateGui)