import sys
import Tkinter

class Style(object):
    COLOR_BG       = 'white'
    BORDER_COLOR   = '222222'
    
    ERROR_COLOR    = 'red'
    OK_COLOR       = 'green'
    
    FONT_HEADER    = ("Helvetica",8,"bold")
    FONT_NORMAL    = ("Helvetica",8,"normal")
    
class OpenLabel(Tkinter.Label):
    def __init__(self,guiParent,text=''):
        Tkinter.Label.__init__(self,guiParent,
                                    text=text,
                                    font=Style.FONT_NORMAL,
                                    bg=Style.COLOR_BG,)
                                    
    def grid(self,row=0,column=0):
        Tkinter.Label.grid(self,row=row,
                               column=column,
                               sticky=Tkinter.W)

class OpenButton(Tkinter.Button):
    def __init__(self,guiParent,text,command):
        Tkinter.Button.__init__(self,guiParent,
                                     text=text,
                                     command=command,
                                     font=Style.FONT_NORMAL,
                                     bg=Style.COLOR_BG,)
                                    
    def grid(self,row=0,column=0,columnspan=1):
        Tkinter.Button.grid(self,row=row,
                                 column=column,
                                 columnspan=columnspan,
                                 sticky=Tkinter.W)
    
class OpenCheckbox(Tkinter.Checkbutton):
    '''
    Provides a checkbox control, initially turned off. Use setState() 
    for programmatic control.
    '''
    def __init__(self,guiParent,text='',variable=None,cb=None):
        '''
        cb is a callback that must accept a single boolean argument for
        the state of the checkbox, where True means the checkbox is checked.
        '''
        self.checkVar = Tkinter.IntVar()
        self.cb       = cb
        Tkinter.Checkbutton.__init__(self,guiParent,
                                    text=text,
                                    variable=self.checkVar,
                                    command=self._guiChanged,
                                    font=Style.FONT_NORMAL,)
                                    
    def grid(self,row=0,column=0):
        Tkinter.Checkbutton.grid(self,row=row,
                               column=column,
                               sticky=Tkinter.W)
                               
    def setState(self,isOn):
        self.checkVar.set(1 if isOn else 0)
        
    def _guiChanged(self):
        if self.cb:
            self.cb(self.checkVar.get() == 1)
    
class HeaderLabel(Tkinter.Label):
    def __init__(self,guiParent,text=''):
        Tkinter.Label.__init__(self,guiParent,
                                    text=text,
                                    font=Style.FONT_HEADER,
                                    bg=Style.COLOR_BG,)
                                    
    def grid(self,row=0,column=0):
        Tkinter.Label.grid(self,row=row,
                               column=column,
                               sticky=Tkinter.W)

class TableCell(Tkinter.Label):

    HEADER = 'header'
    BODY   = 'body'

    def __init__(self,guiParent,cellType,text=''):
    
        if cellType == self.HEADER:
            font = Style.FONT_HEADER
        else:
            font = Style.FONT_NORMAL
        
        Tkinter.Label.__init__(self,guiParent,text=text,
                                              border=1,
                                              bg=Style.COLOR_BG,
                                              relief=Tkinter.RIDGE,
                                              borderwidth=1,
                                              padx=3,
                                              pady=3,
                                              font=font)
    
    def grid(self,row=0,column=0):
        Tkinter.Label.grid(self,row=row,
                               column=column,
                               sticky=Tkinter.W+Tkinter.E)
                                    
class TableBodyCell(Tkinter.Label):
    def __init__(self,guiParent,text=''):
        Tkinter.Label.__init__(self,guiParent,
                                    text=text,
                                    )