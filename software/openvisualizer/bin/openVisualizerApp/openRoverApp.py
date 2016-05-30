import logging
import time
import signal
import os

log = logging.getLogger('openRoverApp')

if __name__=="__main__":
    # Update pythonpath if running in in-tree development mode
    basedir  = os.path.dirname(__file__)
    confFile = os.path.join(basedir, "openvisualizer.conf")
    if os.path.exists(confFile):
        import pathHelper
        pathHelper.updatePath()


from openvisualizer.moteProbe     import moteProbe
from openvisualizer.remoteConnectorRover import remoteConnectorRover



class OpenRoverApp(object):
    '''
    Provides an application model for OpenVisualizer. Provides common,
    top-level functionality for several UI clients.
    '''

    def __init__(self):
        # local variables
        # in "hardware" mode, motes are connected to the serial port
        self.moteProbes       = []
        self.remoteConnector = None


    #======================== public ==========================================

    def close(self):
        '''Closes all thread-based components'''

        log.info('Closing OpenVisualizer')
        for probe in self.moteProbes:
            probe.close()
        if self.remoteConnector :
            self.remoteConnector.close()

    def getMoteProbes(self):
        return self.moteProbes

    def startRemoteConnector(self, PCip, PCport, roverID):
        '''Start the remote connection when infos received by coap server

        :param PCip : ip of the central computer
        :param PCport : port of the connection
        '''
        for probe in self.moteProbes:
            probe.close()
        # in "hardware" mode, motes are connected to the serial port
        self.moteProbes = [
            moteProbe.moteProbe(serialport=p) for p in moteProbe.findSerialPorts()
            ]

        if self.remoteConnector :
            self.remoteConnector.close()
            #leave it time to timeout
            time.sleep(1)
            self.remoteConnector=None
        self.remoteConnector = remoteConnectorRover.remoteConnectorRover(app=self, PCip=PCip, PCport=PCport, roverID=roverID)

#============================ main ============================================
from openvisualizer.remoteConnectorRover import coapserver

if __name__=="__main__":
    print('Initializing OpenVisualizerApp')
    #===== start the app
    app      = OpenRoverApp()
    #===== start the coap server
    c = coapserver.coap.coap()
    c.addResource(coapserver.pcInfo(app))
    #===== add a cli (minimal) interface
    banner  = []
    banner += ['OpenRover']
    banner += ['enter \'q\' to exit']
    banner  = '\n'.join(banner)
    print banner
    while True:
        input = raw_input('> ')
        if input=='q':
            print 'bye bye.'
            app.close()
            os.kill(os.getpid(), signal.SIGTERM)




