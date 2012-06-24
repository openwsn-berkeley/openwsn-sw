import moteProbeSerialThread
import moteProbeSocketThread
import utils
    
class moteProbe(object):
    
    def __init__(self,serialport,socketport):
    
        # store params
        self.serialport = serialport
        self.socketport = socketport
        
        # TODO log
        print "creating moteProbe attaching to "+self.serialport+", listening to TCP port "+str(self.socketport)
        
        # declare serial and socket threads
        self.serialThread = moteProbeSerialThread.moteProbeSerialThread(self.serialport)
        self.socketThread = moteProbeSocketThread.moteProbeSocketThread(self.socketport)
        
        # inform one of another
        self.serialThread.setOtherThreadHandler(self.socketThread)
        self.socketThread.setOtherThreadHandler(self.serialThread)
        
        # start threads
        self.serialThread.start()
        self.socketThread.start()

'''
if this module is run by itself (i.e. not imported from OpenVisualizer),
it has to create moteProbe threads for each mote connected
'''
if __name__ == '__main__':
    
    print 'moteProbe - Open WSN project'    
    serialPortNames     = utils.findSerialPortsNames()
    port_numbers        = [8080+i for i in range(len(serialPortNames))]
    for (serialPortName,port_number) in zip(serialPortNames,port_numbers):
        moteProbe(serialPortName,port_number)
