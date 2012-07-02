import Tkinter

class OpenTableCell(Tkinter.Label):
    
    def __init__(self,guiParent,row,column):
        
        # store params
        self.guiParent = guiParent
        self.row       = row
        self.column    = column
        
        # initialize parent class
        Tkinter.Label.__init__(self,self.guiParent)
        
        # grid
        self.grid(row=self.row,column=self.column)

    def setText(self,newText):
        assert(isinstance(newText,str))
        
        self.configure(text=newText)
    
class OpenTable(Tkinter.Frame):
    
    def __init__(self,guiParent):
        
        # store params
        self.guiParent       = guiParent
        
        # initialize parent class
        Tkinter.Frame.__init__(self)
        
        # local variables
        self.cells           = []
        self.columnNames     = []
    
    #======================== public ==========================================
    
    def update(self,data):
        
        # make sure data is formatted right
        assert(isinstance(data,list))       # data is a list
        for row in data:
            assert(isinstance(row,dict))    # each entry in the list is a dictionnary
        
        # make sure at least one row
        assert(len(data)>0)
        
        # if this is the first call, populate the column names
        if not self.columnNames:
            for k in data[0].keys():
                self.columnNames.append(k)
        
        # make sure each data row contains all columns
        for row in data:
            assert(len(self.columnNames)==len(row))
            for columnName in self.columnNames:
                assert(columnName in row)
        
        # write the header row
        rowCounter = 0
        self._writeRow(0,self.columnNames)
        rowCounter += 1
        
        # write the data rows
        for row in data:
            self._writeRow(rowCounter,[row[columnName] for columnName in self.columnNames])
            rowCounter += 1
        
    #======================== private =========================================
    
    def _writeRow(self,rowCounter,rowData):
        assert(self.columnNames>0)
        
        if len(self.cells)<rowCounter+1:
            self._addRow()
        
        assert(len(self.cells)>=rowCounter+1)
        
        for columnCounter in range(len(rowData)):
            self.cells[rowCounter][columnCounter].setText(rowData[columnCounter])
    
    def _addRow(self):
        assert(self.columnNames>0)
    
        self.cells.append([OpenTableCell(self,len(self.cells),col) for col in range(len(self.columnNames))])

###############################################################################

if __name__=='__main__':
    import OpenWindow

    examplewindow = OpenWindow.OpenWindow("OpenTable")
    
    exampletable  = OpenTable(examplewindow)
    exampletable.grid()
    exampletable.update([
                            {
                                'col1': '1a',
                                'col2': '2a',
                                'col3': '3a',
                            },
                            {
                                'col1': '1b',
                                'col2': '2b',
                                'col3': '3b',
                            },
                        ])
    
    examplewindow.startGui()
