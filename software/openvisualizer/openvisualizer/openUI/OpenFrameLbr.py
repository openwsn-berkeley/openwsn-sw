import OpenFrame
from OpenGuiLib import Style,      \
                       OpenButton, \
                       OpenLabel
import tkFileDialog
import re

class OpenFrameLbr(OpenFrame.OpenFrame):
    
    GUIUPDATEPERIOD = 500
    
    def __init__(self,guiParent,
                      lbrClient,
                      connectParams_cb,
                      width=None,height=None,
                      frameName="connect to the LBR",
                      row=0,column=0,columnspan=1):
        
        # store params
        self.lbrClient        = lbrClient
        self.connectParams_cb = connectParams_cb
        
        # initialize the parent class
        OpenFrame.OpenFrame.__init__(self,guiParent,
                                          width=width,
                                          height=height,
                                          frameName=frameName,
                                          row=row,
                                          column=column,
                                          columnspan=columnspan,)
        
        # local variables
        
        #=====
        
        # connect button
        self.connectButton = OpenButton(self.container,
                                        text='connect',
                                        command=self._retrieveConnectionDetails)
        self.connectButton.grid(row=0,column=0)
        
        #=====
        
        # disconnectReason
        temp = OpenLabel(self.container,
                             text="disconnect reason:")
        temp.grid(row=1,column=0)
        self.disconnectReasonLabel = OpenLabel(self.container)
        self.disconnectReasonLabel.grid(row=1,column=1)
        
        # status
        temp = OpenLabel(self.container,
                             text="status:")
        temp.grid(row=2,column=0)
        self.statusLabel = OpenLabel(self.container)
        self.statusLabel.grid(row=2,column=1)
        
        # prefix
        temp = OpenLabel(self.container,
                             text="prefix:")
        temp.grid(row=3,column=0)
        self.prefixLabel = OpenLabel(self.container)
        self.prefixLabel.grid(row=3,column=1)
        
        # statsTxOk
        temp = OpenLabel(self.container,
                             text="transmitted to LBR:")
        temp.grid(row=4,column=0)
        self.statsTxOkLabel = OpenLabel(self.container)
        self.statsTxOkLabel.grid(row=4,column=1)
        
        # statsTxFailed
        temp = OpenLabel(self.container,
                             text="could not transmit to LBR:")
        temp.grid(row=5,column=0)
        self.statsTxFailedLabel = OpenLabel(self.container)
        self.statsTxFailedLabel.grid(row=5,column=1)
        
        # statsRx
        temp = OpenLabel(self.container,
                             text="received from LBR:")
        temp.grid(row=6,column=0)
        self.statsRxLabel = OpenLabel(self.container)
        self.statsRxLabel.grid(row=6,column=1)
        
        # trigger the update of the stats
        self.after(self.GUIUPDATEPERIOD,self._updateStats)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _updateStats(self):
        
        # get the new stats
        newStats = self.lbrClient.getStats()
        
        # update the labels
        if newStats['disconnectReason']:
            self.disconnectReasonLabel.configure(text=newStats['disconnectReason'])
        else:
            self.disconnectReasonLabel.configure(text='-')
        self.statusLabel.configure(text=newStats['status'])
        if newStats['prefix']:
            self.prefixLabel.configure(text=newStats['prefix'])
        else:
            self.prefixLabel.configure(text='-')
        self.statsTxOkLabel.configure(text="{0} pkts ({1} bytes)".format(
                newStats['packetsSentOk'],
                newStats['bytesSentOk']))
        self.statsTxFailedLabel.configure(text="{0} pkts ({1} bytes)".format(
                newStats['packetsSentFailed'],
                newStats['bytesSentFailed']))
        self.statsRxLabel.configure(text="{0} pkts ({1} bytes)".format(
                newStats['receivedPackets'],
                newStats['receivedBytes']))
    
        # trigger the update of the stats
        self.after(self.GUIUPDATEPERIOD,self._updateStats)
        
    def _retrieveConnectionDetails(self):
        
        # open authentication file
        authFile = tkFileDialog.askopenfile(
                        mode        ='r',
                        title       = 'Select an LBR authentication file',
                        multiple    = False,
                        initialfile = 'guest.lbrauth',
                        filetypes = [
                                        ("LBR authentication file", "*.lbrauth"),
                                        ("All types", "*.*"),
                                    ]
                    )
        if not authFile:
            return
        
        # parse authentication file
        connectParams = {}
        for line in authFile:
            match = re.search('(\S*)\s*=\s*(\S*)',line)
            if match is not None:
                key = match.group(1).strip()
                val = match.group(2).strip()
                try:
                    connectParams[key] = int(val)
                except ValueError:
                    connectParams[key] = val
        
        # call the callback
        self.connectParams_cb(connectParams)

###############################################################################

if __name__=='__main__':

    def _indicateConnectParams(connectParams):
        print "_indicateConnectParams connectParams={0}".format(connectParams)

    import OpenWindow
    
    examplewindow      = OpenWindow.OpenWindow("OpenFrameLbr")
    
    exampleframelbr    = OpenFrameLbr(examplewindow,
                                      _indicateConnectParams)
    exampleframelbr.show()
    
    examplewindow.startGui()
