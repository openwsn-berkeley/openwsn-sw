import Tkinter
import OpenGuiLib

class OpenFrame(Tkinter.Frame):
    
    PADDING = 3
    
    def __init__(self,guiParent,width=None,height=None,frameName="frame",row=0,column=0,columnspan=1):
        
        # store params
        self.guiParent       = guiParent
        self.width           = width
        self.height          = height
        self.frameName       = frameName
        self.row             = row
        self.column          = column
        self.columnspan      = columnspan
        
        # initialize the parent class
        Tkinter.Frame.__init__(self,self.guiParent,
                                    width=self.width,
                                    height=self.height,
                                    bg=OpenGuiLib.Style.COLOR_BG)
        
        # gui layout
        temp                 = OpenGuiLib.HeaderLabel(self,text=frameName)
        temp.grid(row=0,column=0)
        self.container       = Tkinter.Frame(self)
        self.container.grid(row=1,column=0)
    
    #======================== public ==========================================
    
    def show(self):
        self.grid(row=self.row,
                  column=self.column,
                  columnspan=self.columnspan,
                  padx=self.PADDING,
                  pady=self.PADDING)
    
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
