import sys
import Tkinter

class Style(object):
    COLOR_BG       = 'white'
    BORDER_COLOR   = '222222'
    
    FONT_HEADER    = ("Helvetica",8,"bold")
    FONT_NORMAL    = ("Helvetica",8,"normal")
    
    
class HeaderLabel(Tkinter.Label):
    def __init__(self,guiParent,text=''):
        Tkinter.Label.__init__(self,guiParent,
                                    text=text,
                                    font=Style.FONT_HEADER,)
                                    
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