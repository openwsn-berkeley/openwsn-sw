# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

"""
Contains application model for OpenVisualizer. Expects to be called by 
top-level UI module.  See main() for startup use.
"""
import sys
import os
import logging
log = logging.getLogger('openVisualizerApp')

from eventBus      import eventBusMonitor
from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from RPL           import RPL
from openLbr       import openLbr
from openTun       import openTun
from RPL           import UDPLatency
from RPL           import topology

import openvisualizer_utils as u
    
class OpenVisualizerApp(object):
    """
    OpenVisualizer supports both a GUI and a CLI interface, and 
    OpenVisualizerApp provides a single location for common functionality.
    """
    
    def __init__(self,appDir,fwDir,simulatorMode,numMotes,trace):
        
        # store params
        self.appDir               = appDir
        self.fwDir                = fwDir
        self.simulatorMode        = simulatorMode
        self.numMotes             = numMotes
        self.trace                = trace 
        
        # local variables
        self.eventBusMonitor      = eventBusMonitor.eventBusMonitor()
        self.openLbr              = openLbr.OpenLbr()
        self.rpl                  = RPL.RPL()
        self.topology             = topology.topology()
        self.udpLatency           = UDPLatency.UDPLatency()
        self.openTun              = openTun.create() # call last since indicates prefix
        if self.simulatorMode:
            from SimEngine import SimEngine, MoteHandler
            
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
            
            MoteHandler.readNotifIds(
                os.path.join(self.fwDir,'firmware','openos','bsp','boards','python','openwsnmodule_obj.h'))
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
            logging.config.fileConfig(os.path.join(appDir,'trace.conf'), {'logDir': appDir})
            OVtracer.OVtracer()
        
    #======================== public ==========================================
    
    def close(self):
        """Closes all thread-based components"""
        
        log.info('Closing OpenVisualizer')
        self.openTun.close()
        self.rpl.close()
        for probe in self.moteProbes:
            probe.close()
    
       
    #======================== GUI callbacks ===================================

#============================ main ============================================
import logging.config
from argparse       import ArgumentParser

DEFAULT_MOTE_COUNT = 3

def main():
    """
    Entry point for application startup by UI. Parses common arguments.
    
    :rtype:         openVisualizerApp object
    """
    parser   = _createCliParser()
    argspace = parser.parse_args()
    
    logging.config.fileConfig(
        os.path.join(argspace.appDir,'logging.conf'), 
        {'logDir': argspace.appDir}
    )

    if argspace.numMotes > 0:
        # --simCount implies --sim
        argspace.simulatorMode = True
    elif argspace.simulatorMode == True:
        # default count when --simCount not provided
        argspace.numMotes = DEFAULT_MOTE_COUNT

    log.info('Initializing OpenVisualizerApp with options: \n\t{0}'.format(
            '\n\t'.join(['appDir   = {0}'.format(argspace.appDir),
                         'fwDir    = {0}'.format(argspace.fwDir),
                         'sim      = {0}'.format(argspace.simulatorMode),
                         'simCount = {0}'.format(argspace.numMotes),
                         'trace    = {0}'.format(argspace.trace)],
            )))
        
    return OpenVisualizerApp(
        argspace.appDir,
        argspace.fwDir,
        argspace.simulatorMode,
        argspace.numMotes,
        argspace.trace
    )    

def _createCliParser():
    
    parser = ArgumentParser()
    
    parser.add_argument( '-d',
        dest       = 'appDir',
        default    = '.',
        action     = 'store',
        help       = 'working directory'
    )
    
    parser.add_argument( '-f',
        dest       = 'fwDir',
        default    = os.path.join('..','..','..','..','..','openwsn-fw'),
        action     = 'store',
        help       = 'firmware directory'
    )
    
    parser.add_argument( '--sim', '-s',
        dest       = 'simulatorMode',
        default    = False,
        action     = 'store_true',
        help       = 'simulation mode, with default of {0} motes'.format(DEFAULT_MOTE_COUNT)
    )
    
    parser.add_argument( '--simCount', '-n',
        dest       = 'numMotes',
        type       = int,
        default    = 0,
        help       = 'simulation mode, with provided mote count'
    )
    
    parser.add_argument( '--trace','-t',
        dest       = 'trace',
        default    = False,
        action     = 'store_true',
        help       = 'enables memory debugging'
    )
    
    return parser
