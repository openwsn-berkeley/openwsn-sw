#!/usr/bin/python

import Tkinter
from SimStyle import SimStyle
import SimFrame

class SimTimebar(SimFrame.SimFrame):
    
    TIMELABEL_UPDATE_PERIOD = 200
    
    def __init__(self,engine):
        
        # store params
        self.engine = engine
        
        # init parent
        SimFrame.SimFrame.__init__(self)
        
        # startstop button
        self.startstopButton = Tkinter.Button(self,
                                          text='pause',
                                          command=self._pauseButtonPressed)
        self.startstopButton.grid(row=0,column=0)
        
        # current time
        self.currentTimeLabel = Tkinter.Label(self)
        self.currentTimeLabel.after(self.TIMELABEL_UPDATE_PERIOD,self._updateCurrenttime)
        self.currentTimeLabel.grid(row=0,column=1)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _pauseButtonPressed(self):
        
        # pause the engine
        self.engine.pause()
        
        # update button
        self.startstopButton.configure(text='resume')
        self.startstopButton.configure(command=self._resumeButtonPressed)
    
    def _resumeButtonPressed(self):
        
        # resume the engine
        self.engine.resume()
        
        # update button
        self.startstopButton.configure(text='pause')
        self.startstopButton.configure(command=self._pauseButtonPressed)
    
    def _updateCurrenttime(self):
        
        # update the current time label
        self.currentTimeLabel.configure(text='currentTime={0:.3f}'.format(self.engine.timeline.getCurrentTime()))
        
        # schedule the next update
        self.currentTimeLabel.after(self.TIMELABEL_UPDATE_PERIOD,self._updateCurrenttime)