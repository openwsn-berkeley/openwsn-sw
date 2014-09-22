#!/usr/bin/env python

import os
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here, '..', '..', '..'))                       # root/
sys.path.insert(0, os.path.join(here, '..'))                                   # openLbr/
sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))   # PyDispatcher-2.0.3/

import logging
import logging.handlers
import json

import pytest

import openLbr
import openvisualizer.openvisualizer_utils as u

#============================ logging =========================================

LOGFILE_NAME = 'test_utils.log'

import logging
log = logging.getLogger('test_utils')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

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

#===== expectedBuf2int

EXPECTEDBUF2INT = [
    #           buf          int
    json.dumps(([0x01,0x02], 0x0102)),
    json.dumps(([0xaa,0xbb], 0xaabb)),
]

@pytest.fixture(params=EXPECTEDBUF2INT)
def expectedBuf2int(request):
    return request.param

#===== expectedhex2buf

EXPECTEDHEX2BUF = [
    #           hex          buf
    json.dumps(('abcd',      [0xab,0xcd])),
    json.dumps(('',          [])),
    json.dumps(('aa',        [0xaa])),
]

@pytest.fixture(params=EXPECTEDHEX2BUF)
def expectedhex2buf(request):
    return request.param

#===== expectedbyteinverse

EXPECTEDBYTEINVERSE = [
    #           b    b_inverse
    json.dumps((0x01,0x80)),
    json.dumps((0x02,0x40)),
    json.dumps((0x04,0x20)),
    json.dumps((0x81,0x81)),
]

@pytest.fixture(params=EXPECTEDBYTEINVERSE)
def expectedbyteinverse(request):
    return request.param

#===== expectedformatipv6

EXPECTEDFORMATIPv6 = [
    json.dumps(
        (
            [                                                   # list
                0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
                0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
            ],
            '123:4567:89ab:cdef:fedc:ba98:7654:3210'            # string
        )
    ),
    json.dumps(
        (
            [                                                   # list
                0x01,0x23,0x45,0x67,0x00,0x00,0xcd,0xef,
                0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
            ],
            '123:4567:0:cdef:fedc:ba98:7654:3210'               # string
        )
    ),
    json.dumps(
        (
            [                                                   # list
                0x01,0x23,0x45,0x67,0x00,0x00,0x00,0x00,
                0xfe,0xdc,0xba,0x98,0x76,0x54,0x32,0x10
            ],
            '123:4567:0:0:fedc:ba98:7654:3210'                  # string
        )
    ),
]

@pytest.fixture(params=EXPECTEDFORMATIPv6)
def expectedformatipv6(request):
    return request.param

#============================ helpers =========================================

#============================ tests ===========================================

def test_buf2int(expectedBuf2int):
    
    (expBuf,expInt) = json.loads(expectedBuf2int)
    
    assert u.buf2int(expBuf)==expInt

def test_hex2buf(expectedhex2buf):
    (expHex,expBuf) = json.loads(expectedhex2buf)
    expHex = str(expHex)
    
    assert u.hex2buf(expHex)==expBuf

def test_byteinverse(expectedbyteinverse):
    (b,b_inverse) = json.loads(expectedbyteinverse)
    
    assert u.byteinverse(b)==b_inverse
    assert u.byteinverse(b_inverse)==b

def test_formatIPv6Addr(expectedformatipv6):
    
    (ipv6_list,ipv6_string) = json.loads(expectedformatipv6)
    
    print ipv6_string
    
    assert u.formatIPv6Addr(ipv6_list)==ipv6_string