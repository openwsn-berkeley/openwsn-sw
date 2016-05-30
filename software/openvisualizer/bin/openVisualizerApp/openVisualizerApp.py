# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

'''
Contains application model for OpenVisualizer. Expects to be called by 
top-level UI module.  See main() for startup use.
'''
import sys
import os
import logging
import json

from openvisualizer.OVtracer import OVtracer

log = logging.getLogger('openVisualizerApp')

from openvisualizer.eventBus        import eventBusMonitor
from openvisualizer.moteProbe       import moteProbe
from openvisualizer.moteConnector   import moteConnector
from openvisualizer.moteState       import moteState
from openvisualizer.RPL             import RPL
from openvisualizer.openLbr         import openLbr
from openvisualizer.openTun         import openTun
from openvisualizer.RPL             import UDPLatency
from openvisualizer.RPL             import topology
from openvisualizer                 import appdirs
from openvisualizer.remoteConnectorServer   import remoteConnectorServer

import openvisualizer.openvisualizer_utils as u
    
class OpenVisualizerApp(object):
    '''
    Provides an application model for OpenVisualizer. Provides common,
    top-level functionality for several UI clients.
    '''
    
    def __init__(self,confdir,datadir,logdir,simulatorMode,numMotes,trace,debug,simTopology,iotlabmotes, pathTopo, roverMode):
        
        # store params
        self.confdir              = confdir
        self.datadir              = datadir
        self.logdir               = logdir
        self.simulatorMode        = simulatorMode
        self.numMotes             = numMotes
        self.trace                = trace
        self.debug                = debug
        self.iotlabmotes          = iotlabmotes
        self.pathTopo             = pathTopo
        self.roverMode            = roverMode

        # local variables
        self.eventBusMonitor      = eventBusMonitor.eventBusMonitor()
        self.openLbr              = openLbr.OpenLbr()
        self.rpl                  = RPL.RPL()
        self.topology             = topology.topology()
        self.udpLatency           = UDPLatency.UDPLatency()
        self.DAGrootList          = []
        # create openTun call last since indicates prefix
        self.openTun              = openTun.create() 
        if self.simulatorMode:
            from openvisualizer.SimEngine import SimEngine, MoteHandler
            
            self.simengine        = SimEngine.SimEngine(simTopology)
            self.simengine.start()
        
        # import the number of motes from json file given by user (if the pathTopo option is enabled)
        if self.pathTopo and self.simulatorMode:
            try:
                topoConfig = open(pathTopo)
                topo = json.load(topoConfig)
                self.numMotes = len(topo['motes'])
            except Exception as err:
                print err
                app.close()
                os.kill(os.getpid(), signal.SIGTERM)

        
        # create a moteProbe for each mote
        if self.simulatorMode:
            # in "simulator" mode, motes are emulated
            sys.path.append(os.path.join(self.datadir, 'sim_files'))
            import oos_openwsn
            
            MoteHandler.readNotifIds(os.path.join(self.datadir, 'sim_files', 'openwsnmodule_obj.h'))
            self.moteProbes       = []
            for _ in range(self.numMotes):
                moteHandler       = MoteHandler.MoteHandler(oos_openwsn.OpenMote())
                self.simengine.indicateNewMote(moteHandler)
                self.moteProbes  += [moteProbe.moteProbe(emulatedMote=moteHandler)]
        elif self.iotlabmotes:
            # in "IoT-LAB" mode, motes are connected to TCP ports
            
            self.moteProbes       = [
                moteProbe.moteProbe(iotlabmote=p) for p in self.iotlabmotes.split(',')
            ]
            
        else:
            # in "hardware" mode, motes are connected to the serial port

            self.moteProbes       = [
                moteProbe.moteProbe(serialport=p) for p in moteProbe.findSerialPorts()
            ]
        
        # create a moteConnector for each moteProbe
        self.moteConnectors       = [
            moteConnector.moteConnector(mp.getPortName()) for mp in self.moteProbes
        ]
        
        # create a moteState for each moteConnector
        self.moteStates           = [
            moteState.moteState(mc) for mc in self.moteConnectors
        ]

        if self.roverMode :
            self.remoteConnectorServer = remoteConnectorServer.remoteConnectorServer()


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

       
        # import the topology from the json file
        if self.pathTopo and self.simulatorMode:
            
            # delete each connections automatically established during motes creation
            ConnectionsToDelete = self.simengine.propagation.retrieveConnections()
            for co in ConnectionsToDelete :
                fromMote = int(co['fromMote'])
                toMote = int(co['toMote'])
                self.simengine.propagation.deleteConnection(fromMote,toMote)

            motes = topo['motes']
            for mote in motes :
                mh = self.simengine.getMoteHandlerById(mote['id'])
                mh.setLocation(mote['lat'], mote['lon'])
            
            # implements new connections
            connect = topo['connections']
            for co in connect:
                fromMote = int(co['fromMote'])
                toMote = int(co['toMote'])
                pdr = float(co['pdr'])
                self.simengine.propagation.createConnection(fromMote,toMote)
                self.simengine.propagation.updateConnection(fromMote,toMote,pdr)
            
            # store DAGroot moteids in DAGrootList
            DAGrootL = topo['DAGrootList']
            for DAGroot in DAGrootL :
                hexaDAGroot = hex(DAGroot)
                hexaDAGroot = hexaDAGroot[2:]
                prefixLen = 4 - len(hexaDAGroot)
                
                prefix =""
                for i in range(prefixLen):
                    prefix += "0"
                moteid = prefix+hexaDAGroot
                self.DAGrootList.append(moteid)
        
        # start tracing threads
        if self.trace:
            import openvisualizer.OVtracer
            logging.config.fileConfig(
                                os.path.join(self.confdir,'trace.conf'),
                                {'logDir': _forceSlashSep(self.logdir, self.debug)})
            OVtracer.OVtracer()
        
    #======================== public ==========================================
    
    def close(self):
        '''Closes all thread-based components'''
        
        log.info('Closing OpenVisualizer')
        self.openTun.close()
        self.rpl.close()
        for probe in self.moteProbes:
            probe.close()
                
    def getMoteState(self, moteid):
        '''
        Returns the moteState object for the provided connected mote.
        
        :param moteid: 16-bit ID of mote
        :rtype:        moteState or None if not found
        '''
        for ms in self.moteStates:
            idManager = ms.getStateElem(ms.ST_IDMANAGER)
            if idManager and idManager.get16bAddr():
                addr = ''.join(['%02x'%b for b in idManager.get16bAddr()])
                if addr == moteid:
                    return ms
        else:
            return None

    def refreshRoverMotes(self, roverMotes):
        '''Connect the list of roverMotes to openvisualiser.

        :param roverMotes : list of the roverMotes to add
        '''
        # create a moteConnector for each roverMote
        for roverIP, value in roverMotes.items() :
            if not isinstance(value , str):
                for rm in roverMotes[roverIP] :
                        exist = False
                        for mc in self.moteConnectors :
                            if mc.serialport == rm :
                                exist = True
                                break
                        if not exist :
                            moc = moteConnector.moteConnector(rm)
                            self.moteConnectors       += [moc]
                            self.moteStates += [moteState.moteState(moc)]
        self.remoteConnectorServer.initRoverConn(roverMotes)

    def removeRoverMotes(self, roverIP, moteList):
        ''' Remove moteconnect and motestates from list (NOT implemented: quit())
            Stop ZMQ connection
        :param roverIP
        '''

        for moteid in moteList:
            ms = self.getMoteState(moteid)
            if ms:
                self.moteConnectors.remove(ms.moteConnector)
                self.moteStates.remove(ms)
            else:
                for mss in self.moteStates:
                    if moteid == mss.moteConnector.serialport:
                        self.moteConnectors.remove(mss.moteConnector)
                        self.moteStates.remove(mss)
        self.remoteConnectorServer.closeRoverConn(roverIP)



    def getMoteDict(self):
        '''
        Returns a dictionary with key-value entry: (moteid: serialport)
        '''
        moteDict = {}
        for ms in self.moteStates:
            addr = ms.getStateElem(moteState.moteState.ST_IDMANAGER).get16bAddr()
            if addr:
                moteDict[''.join(['%02x' % b for b in addr])] = ms.moteConnector.serialport
            else:
                moteDict[ms.moteConnector.serialport] = None
        return moteDict


#============================ main ============================================
import logging.config
from argparse       import ArgumentParser

DEFAULT_MOTE_COUNT = 3

def main(parser=None, roverMode=False):
    '''
    Entry point for application startup by UI. Parses common arguments.
    
    :param parser:  Optional ArgumentParser passed in from enclosing UI module
                    to allow that module to pre-parse specific arguments
    :rtype:         openVisualizerApp object
    '''
    if parser is None:
        parser = ArgumentParser()
        
    _addParserArgs(parser)
    argspace = parser.parse_args()
    
    confdir, datadir, logdir = _initExternalDirs(argspace.appdir, argspace.debug)
    
    # Must use a '/'-separated path for log dir, even on Windows.
    logging.config.fileConfig(
        os.path.join(confdir,'logging.conf'), 
        {'logDir': _forceSlashSep(logdir, argspace.debug)}
    )

    if argspace.pathTopo:
        argspace.simulatorMode = True
        argspace.numMotes = 0
        argspace.simTopology = "fully-meshed"
        # --pathTopo
    elif argspace.numMotes > 0:
        # --simCount implies --sim
        argspace.simulatorMode = True
    elif argspace.simulatorMode:
        # default count when --simCount not provided
        argspace.numMotes = DEFAULT_MOTE_COUNT

    log.info('Initializing OpenVisualizerApp with options:\n\t{0}'.format(
            '\n    '.join(['appdir   = {0}'.format(argspace.appdir),
                           'sim      = {0}'.format(argspace.simulatorMode),
                           'simCount = {0}'.format(argspace.numMotes),
                           'trace    = {0}'.format(argspace.trace),
                           'debug    = {0}'.format(argspace.debug)],
            )))
    log.info('Using external dirs:\n\t{0}'.format(
            '\n    '.join(['conf     = {0}'.format(confdir),
                           'data     = {0}'.format(datadir),
                           'log      = {0}'.format(logdir)],
            )))
    log.info('sys.path:\n\t{0}'.format('\n\t'.join(str(p) for p in sys.path)))
        
    return OpenVisualizerApp(
        confdir         = confdir,
        datadir         = datadir,
        logdir          = logdir,
        simulatorMode   = argspace.simulatorMode,
        numMotes        = argspace.numMotes,
        trace           = argspace.trace,
        debug           = argspace.debug,
        simTopology     = argspace.simTopology,
        iotlabmotes     = argspace.iotlabmotes,
        pathTopo        = argspace.pathTopo,
        roverMode       = roverMode
    )

def _addParserArgs(parser):
    parser.add_argument('-a', '--appDir', 
        dest       = 'appdir',
        default    = '.',
        action     = 'store',
        help       = 'working directory'
    )
    parser.add_argument('-s', '--sim', 
        dest       = 'simulatorMode',
        default    = False,
        action     = 'store_true',
        help       = 'simulation mode, with default of {0} motes'.format(DEFAULT_MOTE_COUNT)
    )
    parser.add_argument('-n', '--simCount', 
        dest       = 'numMotes',
        type       = int,
        default    = 0,
        help       = 'simulation mode, with provided mote count'
    )
    parser.add_argument('-t', '--trace',
        dest       = 'trace',
        default    = False,
        action     = 'store_true',
        help       = 'enables memory debugging'
    )
    parser.add_argument('-st', '--simTopology',
        dest       = 'simTopology',
        default    = '',
        action     = 'store',
        help       = 'force a certain toplogy (simulation mode only)'
    )
    parser.add_argument('-d', '--debug',
        dest       = 'debug',
        default    = False,
        action     = 'store_true',
        help       = 'enables application debugging'
    )
    parser.add_argument('-iotm', '--iotlabmotes',
        dest       = 'iotlabmotes',
        default    = '',
        action     = 'store',
        help       = 'comma-separated list of IoT-LAB motes (e.g. "wsn430-9,wsn430-34,wsn430-3")'
    )
    parser.add_argument('-i', '--pathTopo', 
        dest       = 'pathTopo',
        default    = '',
        action     = 'store',
        help       = 'a topology can be loaded from a json file'
    )


def _forceSlashSep(ospath, debug):
    '''
    Converts a Windows-based path to use '/' as the path element separator.
    
    :param ospath: A relative or absolute path for the OS on which this process
                   is running
    :param debug:  If true, print extra logging info
    '''
    if os.sep == '/':
        return ospath
        
    head     = ospath
    pathlist = []
    while True:
        head, tail = os.path.split(head)
        if tail == '':
            pathlist.insert(0, head.rstrip('\\'))
            break
        else:
            pathlist.insert(0, tail)
            
    pathstr = '/'.join(pathlist)
    if debug:
        print pathstr
    return pathstr
    
def _initExternalDirs(appdir, debug):    
    '''
    Find and define confdir for config files and datadir for static data. Also
    return logdir for logs. There are several possiblities, searched in the order
    described below.

    1. Provided from command line, appdir parameter
    2. In the directory containing openVisualizerApp.py
    3. In native OS site-wide config and data directories
    4. In the openvisualizer package directory

    The directories differ only when using a native OS site-wide setup.
    
    :param debug: If true, print extra logging info
    :returns: 3-Tuple with config dir, data dir, and log dir
    :raises: RuntimeError if files/directories not found as expected
    '''
    if not appdir == '.':
        if not _verifyConfpath(appdir):
            raise RuntimeError('Config file not in expected directory: {0}'.format(appdir))
        if debug:
            print 'App data found via appdir'
        return appdir, appdir, appdir
    
    filedir = os.path.dirname(__file__)
    if _verifyConfpath(filedir):
        if debug:
            print 'App data found via openVisualizerApp.py'
        return filedir, filedir, filedir
        
    confdir      = appdirs.site_config_dir('openvisualizer', 'OpenWSN')
    # Must use system log dir on Linux since running as superuser.
    linuxLogdir  = '/var/log/openvisualizer'
    if _verifyConfpath(confdir):
        if not sys.platform.startswith('linux'):
            raise RuntimeError('Native OS external directories supported only on Linux')
            
        datadir = appdirs.site_data_dir('openvisualizer', 'OpenWSN')
        logdir  = linuxLogdir
        if os.path.exists(datadir):
            if not os.path.exists(logdir):
                os.mkdir(logdir)
            if debug:
                print 'App data found via native OS'
            return confdir, datadir, logdir
        else:
            raise RuntimeError('Cannot find expected data directory: {0}'.format(datadir))

    datadir = os.path.join(os.path.dirname(u.__file__), 'data')
    if _verifyConfpath(datadir):
        if sys.platform == 'win32':
            logdir = appdirs.user_log_dir('openvisualizer', 'OpenWSN', opinion=False)
        else:
            logdir = linuxLogdir
        if not os.path.exists(logdir):
            # Must make intermediate directories on Windows
            os.makedirs(logdir)
        if debug:
            print 'App data found via openvisualizer package'
            
        return datadir, datadir, logdir
    else:
        raise RuntimeError('Cannot find expected data directory: {0}'.format(datadir))
                    
def _verifyConfpath(confdir):
    '''
    Returns True if OpenVisualizer conf files exist in the provided 
    directory.
    '''
    confpath = os.path.join(confdir, 'openvisualizer.conf')
    return os.path.isfile(confpath)
