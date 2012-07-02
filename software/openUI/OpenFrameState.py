import OpenFrame
import OpenTable
import Tkinter

class OpenFrameState(OpenFrame.OpenFrame):
    
    def __init__(self,guiParent,width=None,height=None,frameName="frame",row=0,column=0):
        
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
                                          column=column)
        
        # local variables
        self.updatePeriod    = None
        
        # metadata label
        temp = Tkinter.Label(self,text="data")
        temp.grid(row=0,column=0)
        
        self.data = OpenTable.OpenTable(self)
        self.data.grid(row=1,column=0)
        
        temp = Tkinter.Label(self,text="meta")
        temp.grid(row=2,column=0)
        
        self.meta = OpenTable.OpenTable(self)
        self.meta.grid(row=3,column=0)
        
    #======================== public ==========================================
    
    def startAutoUpdate(self,updatePeriod,updateFunc,updateParams):
        self.updatePeriod    = updatePeriod
        self.updateFunc      = updateFunc
        self.updateParams    = updateParams
        
        self.after(self.updatePeriod,self._cb_autoUpdate)
    
    def stopAutoUpdate(self):
        self.updatePeriod    = None
    
    def update(self,dataAndMeta):
        
        assert(isinstance(dataAndMeta,dict))
        assert('meta' in dataAndMeta)
        assert(isinstance(dataAndMeta['meta'],(list,dict)))
        assert('data' in dataAndMeta)
        assert(isinstance(dataAndMeta['data'],(list,dict)))
        
        self.data.update([dataAndMeta['data']])
        self.meta.update([dataAndMeta['meta']])
    
    #======================== private =========================================
    
    def _cb_autoUpdate(self):
        
        self.update(self.updateFunc(*self.updateParams).getData())
        
        if self.updatePeriod:
            self.after(self.updatePeriod,self._cb_autoUpdate)
    
###############################################################################

if __name__=='__main__':
    import OpenWindow

    examplewindow      = OpenWindow.OpenWindow("OpenFrameState")
    
    exampleframestate  = OpenFrameState(examplewindow,
                                       frameName='exampleframestate',
                                       row=0,
                                       column=0)
    exampleframestate.show()
    exampleframestate.update(
        {
            'data': {
                        'data1': 'dA1',
                        'data2': 'dA2',
                        'data3': 'dA3',
                    },
            'meta': {
                        'meta1': 'm1',
                        'meta2': 'm2',
                    },
        }
    )
    
    examplewindow.startGui()    
