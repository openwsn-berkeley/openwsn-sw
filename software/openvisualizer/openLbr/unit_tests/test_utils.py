#!/usr/bin/env python

import os
import sys
temp_path = sys.path[0]
sys.path.insert(0, os.path.join(temp_path, '..', '..'))

import logging
import logging.handlers
import json

import pytest

from openLbr import openLbr
import openvisualizer_utils as u

#============================ logging =========================================

LOGFILE_NAME = 'test_utils.log'

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('test_utils')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

logHandler = logging.handlers.RotatingFileHandler(LOGFILE_NAME,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['test_utils',
                   'openLbr',]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
#============================ defines =========================================

#============================ fixtures ========================================

EXPECTEDBUF2INT = [
    #           buf          int
    json.dumps(([0x01,0x02], 0x0102)),
    json.dumps(([0xaa,0xbb], 0xaabb)),
]

@pytest.fixture(params=EXPECTEDBUF2INT)
def expectedBuf2int(request):
    return request.param

#============================ helpers =========================================

#============================ tests ===========================================

def test_sourceRoute(expectedBuf2int):
    
    (expBuf,expInt) = json.loads(expectedBuf2int)
    
    assert openLbr.OpenLbr._buf2int(expBuf)==expInt

def test_byteinverse():
    assert u.byteinverse(0x01)==0x80
    assert u.byteinverse(0x02)==0x40
    assert u.byteinverse(0x04)==0x20
    assert u.byteinverse(0x81)==0x81