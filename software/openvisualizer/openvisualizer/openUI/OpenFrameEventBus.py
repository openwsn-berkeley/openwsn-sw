import json

import OpenFrame
import OpenGuiLib
import OpenTable
import openvisualizer.openvisualizer_utils as u

class OpenFrameEventBus(OpenFrame.OpenFrame):
    
    GUIUPDATEPERIOD = 1000
    
    def __init__(self,guiParent,eventBusMonitor,width=None,height=None,frameName="eventBus",row=0,column=0,columnspan=1):
        
        # store params
        self.guiParent       = guiParent
        self.eventBusMonitor = eventBusMonitor
        self.frameName       = frameName
        self.row             = row
        self.column          = column
        
        # initialize the parent class
        OpenFrame.OpenFrame.__init__(self,
            guiParent,
            width=width,
            height=height,
            frameName=frameName,
            row=row,
            column=column,
            columnspan=columnspan,
        )
        
        # local variables
        self.dataTable = OpenTable.OpenTable(self.container)
        self.dataTable.grid(row=1,column=0)
        
        self.zepToggle = OpenGuiLib.OpenCheckbox(self.container,
                                text='Export bytesToMesh packets as ZEP on TUN interface',
                                cb=eventBusMonitor.setWiresharkDebug)
                                
        self.zepToggle.setState(self.eventBusMonitor.wiresharkDebugEnabled)
        self.zepToggle.grid(row=2,column=0)
        
        # trigger the update of the stats
        self.after(self.GUIUPDATEPERIOD,self._updateStats)
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _updateStats(self):
        
        # load stats
        newStats = json.loads(self.eventBusMonitor.getStats())
        
        for i in range(len(newStats)):
            if type(newStats[i]['signal'])==list and len(newStats[i]['signal'])==3:
                [ip,tran,port] = newStats[i]['signal']
                signal  = []
                signal += [u.formatIPv6Addr(ip)]
                signal += [tran]
                signal += [str(port)]
                newStats[i]['signal'] = ','.join(signal)
        
        # update table
        self.dataTable.update(
            newStats,
            columnOrder = [
                'sender',
                'signal',
                'num',
            ]
        )
        # update in case changed by something besides GUI
        self.zepToggle.setState(self.eventBusMonitor.wiresharkDebugEnabled)
        
        # schedule next update
        self.after(self.GUIUPDATEPERIOD,self._updateStats)
    
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
