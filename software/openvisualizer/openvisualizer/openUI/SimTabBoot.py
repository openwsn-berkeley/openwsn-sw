#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle
import SimTab

class SimTabBoot(SimTab.SimTab):
    
    UPDATEPERIOD = 500
    
    def __init__(self,container,engine):
        
        # store params
        self.engine   = engine
        
        # local variables
        self.lines = []
        
        # init parent
        SimTab.SimTab.__init__(self,container,'boot')
        
        self.after(self.UPDATEPERIOD,self._updateGui)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _updateGui(self):
        
        # get number of motes
        nummotes = self.engine.getNumMotes()
        
        # create one line per mote
        while len(self.lines)<nummotes:
            
            newLine = {}
            
            # label
            newLine['label'] = Tkinter.Label(self,text='mote '+str(len(self.lines)))
            newLine['label'].grid(row=len(self.lines),column=0)
            
            # delay
            newLine['delay'] = Tkinter.Text(self,width=5,height=1)
            newLine['delay'].insert(1.0,"0")
            newLine['delay'].grid(row=len(self.lines),column=1)
            
            # button
            newLine['button'] = Tkinter.Button(self,text='boot',
                                       command=lambda i=len(self.lines):self.bootMote(i))
            newLine['button'].grid(row=len(self.lines),column=2)
            
            self.lines.append(newLine)
        
        # reschedule next update
        self.after(self.UPDATEPERIOD,self._updateGui)
    
    def bootMote(self,rank):
    
        # read the delay
        try:
            bootdelay = float(self.lines[rank]['delay'].get(1.0,Tkinter.END).strip())
        except ValueError:
            self.lines[rank]['delay'].configure(bg=SimStyle.COLOR_ERROR)
            return
        else:
            self.lines[rank]['delay'].configure(bg=SimStyle.COLOR_NOERROR)
        
        # get motehandler for that mote
        moteHandler = self.engine.getMoteHandler(rank)
        
        # schedule the switchOn now
        self.engine.timeline.scheduleEvent(self.engine.timeline.getCurrentTime()+bootdelay,
                                           moteHandler.getId(),
                                           moteHandler.hwSupply.switchOn,
                                           moteHandler.hwSupply.INTR_SWITCHON)
        
        # update button
        self.lines[rank]['button'].configure(state=Tkinter.DISABLED)
        