import sys
import os
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(here, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(here, '..', '..', '..', 'openCli'))    # openCli/

from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from OpenCli       import OpenCli

from eventBus      import eventBusMonitor
from moteState     import moteState
from RPL           import RPL
from openLbr       import openLbr
from openTun       import openTun
from RPL           import UDPLatency
from RPL           import topology

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

class OpenVisualizerCli(OpenCli):
    
    def __init__(self,moteProbe_handlers,moteConnector_handlers,moteState_handlers):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        self.moteConnector_handlers = moteConnector_handlers
        self.moteState_handlers     = moteState_handlers
        
        self.eventBusMonitor      = eventBusMonitor.eventBusMonitor()
        self.openLbr              = openLbr.OpenLbr()
        self.rpl                  = RPL.RPL()
        self.topology             = topology.topology()
        self.udpLatency           = UDPLatency.UDPLatency()
        self.openTun              = openTun.OpenTun() # call last since indicates prefix
    
        # initialize parent class
        OpenCli.__init__(self,"OpenVisualizer CLI",self._quit_cb)
        
        # add commands
        self.registerCommand('list',
                             'l',
                             'list available states',
                             [],
                             self._handlerList)
        self.registerCommand('state',
                             's',
                             'prints some state',
                             ['state parameter'],
                             self._handlerState)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def _handlerList(self,params):
        for ms in self.moteState_handlers:
            output  = []
            output += ['available states:']
            output += [' - {0}'.format(s) for s in ms.getStateElemNames()]
            print '\n'.join(output)
    
    def _handlerState(self,params):
        for ms in self.moteState_handlers:
            try:
                print ms.getStateElem(params[0])
            except ValueError as err:
                print err
    
    #===== helpers
    
    def _quit_cb(self):
        
        for mc in self.moteConnector_handlers:
           mc.quit()
        for mb in self.moteProbe_handlers:
           mb.quit()

def main():
    
    moteProbe_handlers     = []
    moteConnector_handlers = []
    moteState_handlers     = []
    
    # create a moteProbe for each mote connected to this computer
    serialPorts    = moteProbe.findSerialPorts()
    for (serialPort) in serialPorts:
        moteProbe_handlers.append(moteProbe.moteProbe(serialPort))
    
    # create a moteConnector for each moteProbe
    for mp in moteProbe_handlers:
       moteConnector_handlers.append(moteConnector.moteConnector(mp.getSerialPortName()))
    
    # create a moteState for each moteConnector
    for mc in moteConnector_handlers:
       moteState_handlers.append(moteState.moteState(mc))
    
    # create an open CLI
    cli = OpenVisualizerCli(moteProbe_handlers,
                           moteConnector_handlers,
                           moteState_handlers)
    
    cli.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('motesCli.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['moteProbe',
                   'moteConnector',
                   'OpenParser',
                   'Parser',
                   'ParserStatus',
                   'ParserData',
                   'moteState',
                   'OpenCli',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()