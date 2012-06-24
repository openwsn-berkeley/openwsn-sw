import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..', '..'))

from moteProbe  import moteProbe
#from lbrClient  import lbrClient
from processing import shared
from processing import moteConnector
#from processing import openRecord
#from openUI     import openDisplay

def main():
    
    # create one moteProbe per mote connected over serial
    moteProbes          = {}
    moteProbeAddresses  = []
    serialPortNames     = moteProbe.utils.findSerialPortsNames()
    port_number         = 8080
    for serialPortName in serialPortNames:
       moteProbes[serialPortName] = moteProbe.moteProbe(serialPortName,port_number)
       moteProbeAddresses.append(('127.0.0.1',port_number))
       port_number += 1
    
    # declare IPv4/TCP port of each remote moteProbe
    #moteProbeAddresses.append(('75.35.76.214',8080))  #openlbr1,  in Purdue Avenue

    # create a moteConnector for every moteProbe
    for moteProbeAddress in moteProbeAddresses:
       shared.moteConnectors[moteProbeAddress] = moteConnector.moteConnector(moteProbeAddress)
    
    '''
    # create a recordElement and a displayElement for each motePortNetworkThread
    for key,value in shared.moteConnectors.iteritems():
       openRecord.createRecordElement(key)
       openDisplay.createDisplayElement(key)

    # create an lbrClientThread
    shared.lbrClientThread = lbrClient.lbrClientThread(shared.lbrFrame,
                                                       openDisplay.tkSemaphore)
    '''
    # start moteConnectors, then lbrClient, then GUI
    # Note: moteProbes are already started
    for key,value in shared.moteConnectors.iteritems():
       value.start()
    #shared.lbrClientThread.start()
    #openDisplay.startGUI()
    
if __name__=="__main__":
    main()