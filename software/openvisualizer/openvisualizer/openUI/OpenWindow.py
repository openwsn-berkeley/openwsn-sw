import sys
import Tkinter

class OpenWindow(Tkinter.Tk):
    
    def __init__(self,appName,app):
        
        # initialize the parent class
        Tkinter.Tk.__init__(self)
        
        # assign a title to this window
        self.title("{0} - OpenWSN project".format(appName))
        
        # retain a reference to the calling application so we can close
        self.app = app
        
        # set a function to call when "x" close button is pressed
        self.protocol('WM_DELETE_WINDOW',self._closeWindow)
        
        # this window can not be resized
        self.resizable(0,0)
        
        # frames the menu allows you to switch through
        self.menuFrames      = []
        
        # create an (empty) menu
        self.menubar         = Tkinter.Menu(self)
        self.config(menu=self.menubar)
        
    #======================== public ==========================================
    
    def addMenuItem(self,name,frame):
        # parameter validation
        assert type(name)==str
        assert isinstance(frame,Tkinter.Frame)
        
        # add frame to menuFrames
        self.menuFrames.append(frame)
        
        # add menu entry
        temp_lambda = lambda x=frame:self._menuFrameSwitch(x)
        self.menubar.add_command(label=name, command=temp_lambda)
    
    def addMenuList(self,listname,names,frames):
        
        # parameter validation
        assert type(listname)==str
        assert type(names)==list
        for n in names:
            assert type(n)==str
        assert type(frames)==list
        for f in frames:
            assert isinstance(f,Tkinter.Frame)
        assert len(names)==len(frames)
        
        # create list menu
        listMenu = Tkinter.Menu(self.menubar, tearoff=0)
        
        for name,frame in zip(names,frames):
            # add frame to menuFrames
            self.menuFrames.append(frame)
            
            # add menu entry
            temp_lambda = lambda x=frame:self._menuFrameSwitch(x)
            listMenu.add_command(
                label   = name,
                command = temp_lambda,
            )
        
        # add to menuBar
        self.menubar.add_cascade(
            label  = listname,
            menu   = listMenu,
        )
        
        return listMenu
    
    def startGui(self):
        self.mainloop()
    
    #======================== private =========================================
    
    def _menuFrameSwitch(self,frameToSwitchTo):
        for mf in self.menuFrames:
            if mf==frameToSwitchTo:
                mf.grid(row=0)
            else:
                mf.grid_forget()
        self.update_idletasks()
    
    def _closeWindow(self):
        self.app.close()
        self.quit()
    
###############################################################################

if __name__=='__main__':
    window = OpenWindow("OpenWindow")
    window.startGui()