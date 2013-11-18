#!/usr/bin/env python

import os
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here, '..', '..', '..'))               # root/
sys.path.insert(0, os.path.join(here, '..'))                           # moteProbe/

import random
import json

import pytest

import OpenHdlc
import openvisualizer.openvisualizer_utils as u

import logging
import logging.handlers

#============================ logging =========================================

LOGFILE_NAME = 'test_hdlc.log'

import logging
log = logging.getLogger('test_hdlc')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

logHandler = logging.handlers.RotatingFileHandler(LOGFILE_NAME,
                                                  maxBytes=2*1024*1024,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in   [
                        'test_hdlc',
                        'OpenHdlc',
                    ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
#============================ fixtures ========================================

RANDOMFRAME = []
for frameLen in range(1,100,5):
    for run in range(100):
        frame = None
        while (not frame) or (frame in RANDOMFRAME):
            frame = []
            for _ in range(frameLen):
                frame += [random.randint(0x00,0xff)]
        RANDOMFRAME.append(frame)
RANDOMFRAME = [json.dumps(f) for f in RANDOMFRAME]

@pytest.fixture(params=RANDOMFRAME)
def randomFrame(request):
    return request.param

#============================ helpers =========================================

#============================ tests ===========================================

def test_buildRequestFrame():
    
    log.debug("\n---------- test_buildRequestFrame")
    
    hdlc = OpenHdlc.OpenHdlc()
    
    # hdlcify
    frameHdlcified = hdlc.hdlcify('\x53')
    log.debug("request frame: {0}".format(u.formatStringBuf(frameHdlcified)))

def test_dehdlcifyToZero():
    
    log.debug("\n---------- test_dehdlcifyToZero")
    
    hdlc = OpenHdlc.OpenHdlc()
    
    # frame
    frame = [0x53,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa]
    frame = ''.join([chr(b) for b in frame])
    log.debug("frame:      {0}".format(u.formatStringBuf(frame)))
    
    # hdlcify
    frame = hdlc.hdlcify(frame)
    log.debug("hdlcify: {0}".format(u.formatStringBuf(frame)))
    
    # remove flags
    frame = frame[1:-1]
    log.debug("no flags:   {0}".format(u.formatStringBuf(frame)))
    
    # calculate CRC
    crcini     = 0xffff
    crc        = crcini
    for c in frame:
        tmp    = crc^(ord(c))
        crc    = (crc>> 8)^hdlc.FCS16TAB[(tmp & 0xff)]
        log.debug("after {0}, crc={1}".format(hex(ord(c)),hex(crc)))

def test_randdomBackAndForth(randomFrame):
    
    randomFrame = json.loads(randomFrame)
    randomFrame = ''.join([chr(b) for b in randomFrame])
    
    log.debug("\n---------- test_randdomBackAndForth")
    
    hdlc = OpenHdlc.OpenHdlc()
    
    log.debug("randomFrame:    {0}".format(u.formatStringBuf(randomFrame)))
    
    # hdlcify
    frameHdlcified = hdlc.hdlcify(randomFrame)
    log.debug("hdlcified:   {0}".format(u.formatStringBuf(frameHdlcified)))
    
    # dehdlcify
    frameDehdlcified = hdlc.dehdlcify(frameHdlcified)
    log.debug("dehdlcified:    {0}".format(u.formatStringBuf(frameDehdlcified)))
    
    assert frameDehdlcified==randomFrame
