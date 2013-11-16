#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle
import SimFrame

class SimTabcontainer(SimFrame.SimFrame):
    
    def __init__(self):
        
        # local variables
        self.tabs = {}
        
        # init parent
        SimFrame.SimFrame.__init__(self)
        
        # buttons
        self.buttons = Tkinter.Frame(self,width=SimStyle.WIDTH_BUTTON,
                                          height=SimStyle.HEIGHT_CONTAINER,
                                          bg='red')
        self.buttons.grid(row=0,column=0)
        
        # container
        self.container = Tkinter.Frame(self,width=SimStyle.WIDTH_CONTAINER,
                                            height=SimStyle.HEIGHT_CONTAINER)
        self.container.grid(row=0,column=1)
    
    #======================== public ==========================================
    
    def getContainer(self):
        return self.container
    
    def addTab(self,newTab):
        
        # get new tab's name
        name = newTab.getName()
        
        # make sure doesn't exist yet
        assert(name not in self.tabs)
        
        # add button to GUI
        
        newButton = Tkinter.Button(self.buttons,
                                   text=name,
                                   command=lambda:self.switchTabs(name))
        newButton.grid(row=len(self.tabs),column=0)
        
        # add to tabs structure
        self.tabs[name] = {}
        self.tabs[name]['button'] = newButton
        self.tabs[name]['frame']  = newTab
    
    def switchTabs(self,newTabName):
        
        for k,v in self.tabs.items():
            if k in [newTabName]:
                v['button'].configure(bg='blue')
                v['frame'].grid(row=0,column=0)
            else:
                v['button'].configure(bg='red')
                v['frame'].grid_forget()
        
        self.container.configure(width=SimStyle.WIDTH_CONTAINER,
                                 height=SimStyle.HEIGHT_CONTAINER)
    
    #======================== private =========================================
    