#!/usr/bin/env python

import os
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here, '..', '..', '..'))                       # root/
sys.path.insert(0, os.path.join(here, '..'))                                   # RPL/
sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))   # PyDispatcher-2.0.3/

import logging
import logging.handlers
import json

import pytest

import SourceRoute
import topology
import openvisualizer.openvisualizer_utils as u

#============================ logging =========================================

LOGFILE_NAME = 'test_sourceRoute.log'

import logging
log = logging.getLogger('test_sourceRoute')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

logHandler = logging.handlers.RotatingFileHandler(LOGFILE_NAME,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['test_sourceRoute',
                   'SourceRoute',]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
#============================ defines =========================================

MOTE_A = [0xaa]*8
MOTE_B = [0xbb]*8
MOTE_C = [0xcc]*8
MOTE_D = [0xdd]*8

#============================ fixtures ========================================

EXPECTEDSOURCEROUTE = [
    json.dumps((MOTE_B, [MOTE_B,MOTE_A])),
    json.dumps((MOTE_C, [MOTE_C,MOTE_B,MOTE_A])),
    json.dumps((MOTE_D, [MOTE_D,MOTE_C,MOTE_B,MOTE_A])),
]

@pytest.fixture(params=EXPECTEDSOURCEROUTE)
def expectedSourceRoute(request):
    return request.param

#============================ helpers =========================================

#============================ tests ===========================================

def test_sourceRoute(expectedSourceRoute):
    '''
    This tests the following topology
    
    MOTE_A <- MOTE_B <- MOTE_C <- MOTE_D
    '''
    
    sourceRoute = SourceRoute.SourceRoute()
    topo        = topology.topology()
    
    sourceRoute.dispatch(          
        signal          = 'updateParents',
        data            =  (tuple(MOTE_B),[MOTE_A]),
    )
    sourceRoute.dispatch(          
        signal          = 'updateParents',
        data            =  (tuple(MOTE_C),[MOTE_B]),
    )
    sourceRoute.dispatch(          
        signal          = 'updateParents',
        data            =  (tuple(MOTE_D),[MOTE_C]),
    )
    
    expectedDestination = json.loads(expectedSourceRoute)[0]
    expectedRoute       = json.loads(expectedSourceRoute)[1]
    calculatedRoute     = sourceRoute.getSourceRoute(expectedDestination)
    
    # log
    if log.isEnabledFor(logging.DEBUG):
        output          = []
        output         += ['\n']
        output         += ['expectedDestination: {0}'.format(u.formatAddr(expectedDestination))]
        output         += ['expectedRoute:']
        for m in expectedRoute:
            output     += ['- {0}'.format(u.formatAddr(m))]
        output         += ['calculatedRoute:']
        for m in calculatedRoute:
            output     += ['- {0}'.format(u.formatAddr(m))]
        output          = '\n'.join(output)
        log.debug(output)
    
    assert calculatedRoute==expectedRoute
