import json

from EventBus import EventBus

import OpenFrame
import OpenTable

class OpenFrameEventBus(OpenFrame.OpenFrame):
    
    def __init__(self,guiParent,width=None,height=None,frameName="frame",row=0,column=0,columnspan=1):
        
        # store params
        self.guiParent       = guiParent
        self.frameName       = frameName
        self.row             = row
        self.column          = column
        
        # initialize the parent class
        OpenFrame.OpenFrame.__init__(self,guiParent,
                                          width=width,
                                          height=height,
                                          frameName=frameName,
                                          row=row,
                                          column=column,
                                          columnspan=columnspan,)
        
        # local variables
        self.updatePeriod    = None
        
        self.dataTable = OpenTable.OpenTable(self.container)
        self.dataTable.grid(row=1,column=0)
        
    #======================== public ==========================================
    
    def startAutoUpdate(self,updatePeriod):
        self.updatePeriod    = updatePeriod
        
        self.after(self.updatePeriod,self._cb_autoUpdate)
    
    def stopAutoUpdate(self):
        self.updatePeriod    = None
    
    def update(self,newData):
        self.dataTable.update(newData,
                              columnOrder = [
                                  'uri',
                                  'numIn',
                                  'numOut',
                              ])
    
    #======================== private =========================================
    
    def _cb_autoUpdate(self):
        
        self.update(json.loads(EventBus.EventBus().getStats()))
        
        if self.updatePeriod:
            self.after(self.updatePeriod,self._cb_autoUpdate)
    
###############################################################################

if __name__=='__main__':
    import OpenWindow

    examplewindow      = OpenWindow.OpenWindow("OpenFrameEventBus")
    
    exampleframestate  = OpenFrameEventBus(examplewindow,
                                           frameName='exampleframeeventbus',
                                           row=0,
                                           column=0)
    exampleframestate.show()
    exampleframestate.update(
        [
            {
                'data1': 'dA1',
                'data2': 'dB1',
                'data3': 'dC1',
            },
            {
                'data1': 'dA2',
                'data2': 'dB2',
                'data3': 'dC2',
            },
        ]
    )
    
    examplewindow.startGui()
