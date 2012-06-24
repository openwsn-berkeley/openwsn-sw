import shared
import moteProbe
import moteConnector
import openRecord
import lbrClient
import openDisplay

#attach a moteProbe to each mote connected to by serial
moteProbes          = {}
moteProbeAddresses  = []
serialPortNames     = moteProbe.findSerialPortsNames()
port_number         = 8080
for serialPortName in serialPortNames:
   moteProbes[serialPortName] = moteProbe.moteProbe(serialPortName,port_number)
   moteProbeAddresses.append(('127.0.0.1',port_number))
   port_number += 1
#add the IPv4 address and port number of your remote moteProbes here
#moteProbeAddresses.append(('128.32.33.233',8080)) #wsnserver, in 471 Cory
#moteProbeAddresses.append(('128.32.33.129',8080)) #openlbr2,  in 471 Cory
#moteProbeAddresses.append(('75.35.76.214',8080))  #openlbr1,  in Purdue Avenue
#moteProbeAddresses.append(('10.0.0.2',8080))      #openlbr3,  in 471 Cory

# create a moteConnector for every moteProbe
for moteProbeAddress in moteProbeAddresses:
   shared.moteConnectors[moteProbeAddress] = moteConnector.moteConnector(moteProbeAddress)

#create a recordElement and a displayElement for each motePortNetworkThread
for key,value in shared.moteConnectors.iteritems():
   openRecord.createRecordElement(key)
   openDisplay.createDisplayElement(key)

#create an lbrClientThread
shared.lbrClientThread = lbrClient.lbrClientThread(shared.lbrFrame,
                                                   openDisplay.tkSemaphore)

# start moteConnectors, then lbrClient, then GUI
# Note: moteProbes are already started
for key,value in shared.moteConnectors.iteritems():
   value.start()
shared.lbrClientThread.start()
openDisplay.startGUI()