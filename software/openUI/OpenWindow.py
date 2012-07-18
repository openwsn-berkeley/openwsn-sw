import sys
import Tkinter

class OpenWindow(Tkinter.Tk):
    
    def __init__(self,appName):
        
        # initialize the parent class
        Tkinter.Tk.__init__(self)
        
        # assign a title to this window
        self.title("{0} - OpenWSN project".format(appName))
        
        # set a function to call when "x" close button is pressed
        self.protocol('WM_DELETE_WINDOW',self._closeWindow)
        
        # this window can not be resized
        #self.resizable(0,0)
        
    #======================== public ==========================================
    
    def startGui(self):
        self.mainloop()
    
    #======================== private =========================================
    
    def _closeWindow(self):
        # stop the mainloop and close this window
        self.quit()
        
        # TODO: call teardown functions?
        
        # quit
        sys.exit()
    
###############################################################################

if __name__=='__main__':
    window = OpenWindow("OpenWindow")
    window.startGui()