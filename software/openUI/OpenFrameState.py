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
    
    def update(self,dataAndMeta):
        assert('data' in dataAndMeta)
        assert('meta' in dataAndMeta)
        
        self.data.update(dataAndMeta['data'])
        self.meta.update(dataAndMeta['meta'])
    
    #======================== private =========================================
    
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
            'data': [
                        {
                            'data1': 'dA1',
                            'data2': 'dA2',
                            'data3': 'dA3',
                        },
                        {
                            'data1': 'dB1',
                            'data2': 'dB2',
                            'data3': 'dB3',
                        },
                    ],
            'meta': [
                        {
                            'meta1': 'm1',
                            'meta2': 'm2',
                        },
                    ],
        }
    )
    
    examplewindow.startGui()    
