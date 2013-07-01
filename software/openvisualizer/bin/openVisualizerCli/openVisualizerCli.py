import sys
import os
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(here, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(here, '..', '..', '..', 'openCli'))    # openCli/
    sys.path.insert(0, os.path.join(here, '..', '..', '..'))                          # software/
    sys.path.insert(0, os.path.join(here, '..', '..', '..', '..', '..', 'openwsn-fw', 'firmware','openos','projects','common'))


import logging.config


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

from optparse import OptionParser

import openvisualizer_utils as u

from SimEngine import SimEngine, \
                      MoteHandler
from openCli   import SimCli


LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

class OpenVisualizerCli(OpenCli):
    
    def __init__(self,simulatorMode,numMotes,trace):
        
        # store params
        self.simulatorMode        = simulatorMode
        self.numMotes             = numMotes
        self.trace                = trace 
        
        self.eventBusMonitor      = eventBusMonitor.eventBusMonitor()
        self.openLbr              = openLbr.OpenLbr()
        self.rpl                  = RPL.RPL()
        self.topology             = topology.topology()
        self.udpLatency           = UDPLatency.UDPLatency()
        self.openTun              = openTun.create() # call last since indicates prefix
    
        if self.simulatorMode:
            self.simengine        = SimEngine.SimEngine()
            self.simengine.start()
        
        # create a moteProbe for each mote
        if not self.simulatorMode:
            # in "hardware" mode, motes are connected to the serial port      
            self.moteProbes       = [
                moteProbe.moteProbe(serialport=sp) for sp in moteProbe.findSerialPorts()
            ]
        else:
            # in "simulator" mode, motes are emulated
            import oos_openwsn
            self.moteProbes       = []
            for _ in range(self.numMotes):
                moteHandler       = MoteHandler.MoteHandler(self.simengine,oos_openwsn.OpenMote())
                self.simengine.indicateNewMote(moteHandler)
                self.moteProbes  += [moteProbe.moteProbe(emulatedMote=moteHandler)]
        
        # create a moteConnector for each moteProbe
        self.moteConnectors       = [
            moteConnector.moteConnector(mp.getSerialPortName()) for mp in self.moteProbes
        ]
        
        # create a moteState for each moteConnector
        self.moteStates           = [
            moteState.moteState(mc) for mc in self.moteConnectors
        ]
        
        # boot all emulated motes, if applicable
        if self.simulatorMode:
            self.simengine.pause()
            now = self.simengine.timeline.getCurrentTime()
            for rank in range(self.simengine.getNumMotes()):
                moteHandler = self.simengine.getMoteHandler(rank)
                self.simengine.timeline.scheduleEvent(
                    now,
                    moteHandler.getId(),
                    moteHandler.hwSupply.switchOn,
                    moteHandler.hwSupply.INTR_SWITCHON
                )
            self.simengine.resume()
        
        # start tracing threads
        if self.trace:
            import OVtracer
            appDir = '.'
            logging.config.fileConfig(os.path.join(appDir,'trace.conf'), {'logDir': appDir})
            OVtracer.OVtracer()
    
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
        
        self.registerCommand('root',
                             'r',
                             'sets dagroot',
                             ['serial port'],
                             self._handlerRoot)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def _handlerList(self,params):
        for ms in self.moteStates:
            output  = []
            output += ['available states:']
            output += [' - {0}'.format(s) for s in ms.getStateElemNames()]
            print '\n'.join(output)
    
    def _handlerState(self,params):
        for ms in self.moteStates:
            try:
                print ms.getStateElem(params[0])
            except ValueError as err:
                print err
    
    def _handlerRoot(self,params):
        for ms in self.moteStates:
            try:
                if (ms.moteConnector.serialport==params[0]):
                    ms.triggerAction(moteState.moteState.TRIGGER_DAGROOT)
                
                
            except ValueError as err:
                print err
    
    
    #===== helpers
    
    def _quit_cb(self):
        
        for mc in self.moteConnector_handlers:
           mc.quit()
        for mb in self.moteProbe_handlers:
           mb.quit()


def main(simulatorMode,numMotes,trace):

    appDir = '.'
    logging.config.fileConfig(os.path.join(appDir,'logging.conf'), {'logDir': appDir})
    
    # create an open CLI
    cli = OpenVisualizerCli(simulatorMode,numMotes,trace)
    
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
    
def parseCliOptions():
    
    parser = OptionParser()
    
    parser.add_option( '--sim', '-s',
        dest       = 'simulatorMode',
        default    = False,
        action     = 'store_true',
    )
    
    parser.add_option( '-n',
        dest       = 'numMotes',
        type       = 'int',
        default    = 3,
    )
    
    parser.add_option( '--trace','-t',
        dest       = 'trace',
        default    = False,
        action     = 'store_true',
    )
    
    (opts, args)  = parser.parse_args()
    
    return opts

if __name__=="__main__":
    
    opts = parseCliOptions()
    args = opts.__dict__
    
    main(
        simulatorMode   = args['simulatorMode'],
        numMotes        = args['numMotes'],
        trace           = args['trace'],
    )    