import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..', '..'))

from moteProbe     import moteProbe
from moteConnector import moteConnector
#from lbrClient     import lbrClient
#from processing    import openRecord
#from openUI        import openDisplay

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

def main():
    
    moteProbe_handlers     = []
    moteConnector_handlers = []
    moteState_handlers     = []
    
    #===== moteProbe
    
    serialPorts    = moteProbe.utils.findSerialPorts()
    tcpPorts       = [TCP_PORT_START+i for i in range(len(serialPorts))]
    for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
        moteProbe_handlers.append(moteProbe.moteProbe(serialPort,tcpPort))
    
    #===== moteConnector
    
    for temp_moteProbe in moteProbe_handlers:
       moteConnector_handlers.append(moteConnector.moteConnector(LOCAL_ADDRESS,temp_moteProbe.getTcpPort()))
    
    #===== moteState
    
    '''
    # create a recordElement and a displayElement for each motePortNetworkThread
    for key,value in shared.moteConnectors.iteritems():
       openRecord.createRecordElement(key)
       openDisplay.createDisplayElement(key)

    # create an lbrClientThread
    shared.lbrClientThread = lbrClient.lbrClientThread(shared.lbrFrame,
                                                       openDisplay.tkSemaphore)
    '''
    # start moteConnectors, then lbrClient, then GUI (moteProbe are already started)
    for temp_moteConnector in moteConnector_handlers:
       temp_moteConnector.start()
    #shared.lbrClientThread.start()
    #openDisplay.startGUI()
    
if __name__=="__main__":
    main()