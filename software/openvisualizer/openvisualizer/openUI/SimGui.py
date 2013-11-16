#!/usr/bin/python

from SimWindow   import SimWindow
import SimTimebar
import SimTabcontainer
import SimTabBoot
import SimTabStats
import SimTabAbout

class SimGui(object):
    
    def __init__(self,engine):
        
        self.engine = engine
        
        self.window = SimWindow()
        
        #===== tab container
        self.tabcontainer = SimTabcontainer.SimTabcontainer()
        self.tabcontainer.grid(row=0,column=0)
        
        self.tabboot = SimTabBoot.SimTabBoot(self.tabcontainer.getContainer(),
                                             self.engine)
        self.tabcontainer.addTab(self.tabboot)
        
        self.tabstats = SimTabStats.SimTabStats(self.tabcontainer.getContainer(),
                                                self.engine)
        self.tabcontainer.addTab(self.tabstats)
        
        self.tababout = SimTabAbout.SimTabAbout(self.tabcontainer.getContainer())
        self.tabcontainer.addTab(self.tababout)
        
        self.tabcontainer.switchTabs('load')
        
        #===== time bar
        self.timebar = SimTimebar.SimTimebar(self.engine)
        self.timebar.grid(row=1,column=0)
    
    #======================== public ==========================================
    
    def start(self):
        
        self.window.mainloop()
    
    #======================== private =========================================