import json

import OpenFrame
import OpenGuiLib

class OpenFrameButton(OpenFrame.OpenFrame):
    
    def __init__(self,callfunction,callparams,guiParent,width=None,height=None,frameName="frame",buttonText='click',row=0,column=0,columnspan=1):
        
        # store params
        self.guiParent       = guiParent
        self.frameName       = frameName
        self.row             = row
        self.column          = column
        
        # initialize the parent class
        OpenFrame.OpenFrame.__init__(self,
            guiParent        = guiParent,
            width            = width,
            height           = height,
            frameName        = frameName,
            row              = row,
            column           = column,
            columnspan       = columnspan,
        )
        
        # local variables
        temp_lambda = lambda x=callparams:callfunction(*x)
        self.button = OpenGuiLib.OpenButton(
            guiParent        = self.container,
            text             = buttonText,
            command          = temp_lambda,
        )
        self.button.grid(row=0,column=0)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    

###############################################################################

if __name__=='__main__':
    import OpenWindow
    
    def examplecallback(msg):
        print 'button pressed! msg={0}'.format(msg)
    
    examplewindow            = OpenWindow.OpenWindow("OpenFrameState")
    
    exampleframebutton       = OpenFrameButton(
        callfunction         = examplecallback,
        callparams           = ('hello',),
        guiParent            = examplewindow,
        frameName            = 'exampleframebutton',
        buttonText           = 'click here!', 
        row                  = 0,
        column               = 0
    )
    exampleframebutton.show()
    
    examplewindow.startGui()
