import Tkinter

class OpenFrame(Tkinter.Frame):
    
    def __init__(self,guiParent,width=None,height=None,frameName="frame",row=0,column=0):
        
        # store params
        self.guiParent       = guiParent
        self.width           = width
        self.height          = height
        self.frameName       = frameName
        self.row             = row
        self.column          = column
        
        # initialize the parent class
        Tkinter.Frame.__init__(self,self.guiParent,
                                    width=self.width,
                                    height=self.height)
        
    #======================== public ==========================================
    
    def show(self):
        self.grid(row=self.row,column=self.column)
    
    def hide(self):
        self.grid_forget()
    
    #======================== private =========================================
    
###############################################################################

if __name__=='__main__':
    import OpenWindow

    examplewindow = OpenWindow.OpenWindow("OpenFrame")
    
    exampleframe  = OpenFrame(examplewindow,
                              frameName='exampleframe',
                              width=300,
                              height=300,
                              row=0,
                              column=0)
    exampleframe.show()
    
    examplewindow.startGui()
