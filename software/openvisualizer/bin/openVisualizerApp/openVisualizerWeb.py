#!/usr/bin/python
# Copyright (c) 2013, Ken Bannister.
# All rights reserved.
# 
# Released under the BSD 2-Clause license as published at the link below.
# http://opensource.org/licenses/BSD-2-Clause
import sys
import os

if __name__=="__main__":
    # Update pythonpath if running in in-tree development mode
    basedir  = os.path.dirname(__file__)
    confFile = os.path.join(basedir, "openvisualizer.conf")
    if os.path.exists(confFile):
        import pathHelper
        pathHelper.updatePath()

import logging
log = logging.getLogger('openVisualizerWeb')

try:
    from openvisualizer.moteState import moteState
except ImportError:
    # Debug failed lookup on first library import
    print 'ImportError: cannot find openvisualizer.moteState module'
    print 'sys.path:\n\t{0}'.format('\n\t'.join(str(p) for p in sys.path))

import json
import bottle
from bottle        import view

import openVisualizerApp
import openvisualizer.openvisualizer_utils as u

class OpenVisualizerWeb():
    '''
    Provides web UI for OpenVisualizer. Runs as a webapp in a Bottle web
    server.
    '''
        
    def __init__(self,app,websrv):
        '''
        :param app:    OpenVisualizerApp
        :param websrv: Web server
        '''
        log.info('Creating OpenVisualizerWeb')
        
        # store params
        self.app                    = app
        self.websrv                 = websrv
        
        self._defineRoutes()
        
        # To find page templates
        bottle.TEMPLATE_PATH.append('{0}/web_files/templates/'.format(self.app.datadir))
        
    #======================== public ==========================================
    
    #======================== private =========================================
    def _defineRoutes(self):
        '''
        Matches web URL to impelementing method. Cannot use @route annotations
        on the methods due to the class-based implementation.
        '''
        self.websrv.route(path='/',                       callback=self._showMoteview)
        self.websrv.route(path='/moteview',               callback=self._showMoteview)
        self.websrv.route(path='/moteview/:moteid',       callback=self._showMoteview)
        self.websrv.route(path='/motedata/:moteid',       callback=self._getMoteData)
        self.websrv.route(path='/toggle_root/:moteid',    callback=self._toggleRoot)
        self.websrv.route(path='/eventBus',               callback=self._showEventBus)
        self.websrv.route(path='/eventdata',              callback=self._getEventData)
        self.websrv.route(path='/eventDebug/:enabled',    callback=self._setEventDebug)
        self.websrv.route(path='/static/<filepath:path>', callback=self._serverStatic)

    @view('moteview.tmpl')
    def _showMoteview(self, moteid=None):
        '''
        Collects the list of motes, and the requested mote to view.
        
        :param moteid: 16-bit ID of mote (optional)
        '''
        log.debug("moteview moteid parameter is {0}".format(moteid));
        
        motelist = []
        for ms in self.app.moteStates:
            addr = ms.getStateElem(moteState.moteState.ST_IDMANAGER).get16bAddr()
            if addr:
                motelist.append( ''.join(['%02x'%b for b in addr]) )
            else:
                motelist.append(ms.moteConnector.serialport)
        
        tmplData = {
            'motelist'       : motelist,
            'requested_mote' : moteid if moteid else 'none',
        }
        return tmplData
        
    def _serverStatic(self, filepath):
        return bottle.static_file(filepath, 
                                  root='{0}/web_files/static/'.format(self.app.datadir))
        
    def _toggleRoot(self, moteid):
        '''
        Triggers toggle of DAGroot and bridge states, via moteState. No
        real response. Page is updated when next retrieve mote data.
        
        :param moteid: 16-bit ID of mote
        '''
        log.info('Toggle root status for moteid {0}'.format(moteid))
        ms = self.app.getMoteState(moteid)
        if ms:
            log.debug('Found mote {0} in moteStates'.format(moteid))
            ms.triggerAction(ms.TRIGGER_DAGROOT)
            return '{"result" : "success"}'
        else:
            log.debug('Mote {0} not found in moteStates'.format(moteid))
            return '{"result" : "fail"}'
                                  
    def _getMoteData(self, moteid):
        '''
        Collects data for the provided mote.
        
        :param moteid: 16-bit ID of mote
        '''
        log.debug('Get JSON data for moteid {0}'.format(moteid))
        ms = self.app.getMoteState(moteid)
        if ms:
            log.debug('Found mote {0} in moteStates'.format(moteid))
            states = {
                ms.ST_IDMANAGER   : ms.getStateElem(ms.ST_IDMANAGER).toJson('data'),
                ms.ST_ASN         : ms.getStateElem(ms.ST_ASN).toJson('data'),
                ms.ST_ISSYNC      : ms.getStateElem(ms.ST_ISSYNC).toJson('data'),
                ms.ST_MYDAGRANK   : ms.getStateElem(ms.ST_MYDAGRANK).toJson('data'),
                ms.ST_OUPUTBUFFER : ms.getStateElem(ms.ST_OUPUTBUFFER).toJson('data'),
                ms.ST_BACKOFF     : ms.getStateElem(ms.ST_BACKOFF).toJson('data'),
                ms.ST_MACSTATS    : ms.getStateElem(ms.ST_MACSTATS).toJson('data'),
                ms.ST_SCHEDULE    : ms.getStateElem(ms.ST_SCHEDULE).toJson('data'),
                ms.ST_QUEUE       : ms.getStateElem(ms.ST_QUEUE).toJson('data'),
                ms.ST_NEIGHBORS   : ms.getStateElem(ms.ST_NEIGHBORS).toJson('data'),
            }
        else:
            log.debug('Mote {0} not found in moteStates'.format(moteid))
            states = {}
        return states
            
    def _setEventDebug(self, enabled):
        '''
        Selects whether eventBus must export debug packets.
        
        :param enabled: 'true' if enabled; any other value considered false
        '''
        log.info('Enable eventBus debug packets: {0}'.format(enabled))
        self.app.eventBusMonitor.setMeshDebugExport(enabled == 'true')
        return '{"result" : "success"}'

    @view('eventBus.tmpl')
    def _showEventBus(self):
        '''
        Simple page; data for the page template is identical to the data 
        for periodic updates of event list.
        '''
        return self._getEventData()
    
    def _getEventData(self):
        response = {
            'isDebugPkts' : 'true' if self.app.eventBusMonitor.meshDebugEnabled else 'false',
            'stats'       : self.app.eventBusMonitor.getStats(),
        }
        return response

#============================ main ============================================
from argparse       import ArgumentParser

def _addParserArgs(parser):
    '''Adds arguments specific to web UI.'''
    
    parser.add_argument('-H', '--host',
        dest       = 'host',
        default    = '0.0.0.0',
        action     = 'store',
        help       = 'host address'
    )
    
    parser.add_argument('-p', '--port',
        dest       = 'port',
        default    = 8080,
        action     = 'store',
        help       = 'port number'
    )

webapp = None
if __name__=="__main__":
    parser   =  ArgumentParser()
    _addParserArgs(parser)
    argspace = parser.parse_known_args()[0]

    app      = openVisualizerApp.main(parser)
    websrv   = bottle.Bottle()
    webapp   = OpenVisualizerWeb(app, websrv)

    # Must first allow openVisualizerApp to initialize logging.
    log.info('Initializing OpenVisualizerWeb with options: \n\t{0}'.format(
            '\n\t'.join(['host = {0}'.format(argspace.host),
                         'port = {0}'.format(argspace.port)]
            )))
    
    websrv.run(host  = argspace.host, 
               port  = argspace.port, 
               quiet = not app.debug, 
               debug = app.debug)
    
