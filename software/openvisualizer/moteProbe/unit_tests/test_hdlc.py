import os
import sys
cur_path = sys.path[0]
sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
sys.path.insert(0, os.path.join(cur_path, '..'))                           # moteProbe/
sys.path.insert(0, os.path.join(cur_path, '..', '..','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/

import random

import openhdlc
import openvisualizer_utils as u

import logging
import logging.handlers

#============================ logging =========================================

LOGFILE_NAME = 'test_hdlc.log'

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('test_hdlc')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

logHandler = logging.handlers.RotatingFileHandler(LOGFILE_NAME,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in   [
                        'test_hdlc',
                        'openhdlc',
                    ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
#============================ helpers =========================================

#============================ tests ===========================================

def test_buildRequestFrame():
    
    log.debug("\n---------- test_buildRequestFrame")
    
    hdlc = openhdlc.OpenHdlc()
    
    # hdlcify
    frameHdlcified = hdlc.hdlcify('\x53')
    log.debug("request frame: {0}".format(u.formatBuf(frameHdlcified)))

def test_dehdlcifyToZero():
    
    log.debug("\n---------- test_dehdlcifyToZero")
    
    hdlc = openhdlc.OpenHdlc()
    
    # frame
    frame = [0x53,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa]
    frame = ''.join([chr(b) for b in frame])
    log.debug("frame:      {0}".format(u.formatBuf(frame)))
    
    # hdlcify
    frame = hdlc.hdlcify(frame)
    log.debug("hdlcify: {0}".format(u.formatBuf(frame)))
    
    # remove flags
    frame = frame[1:-1]
    log.debug("no flags:   {0}".format(u.formatBuf(frame)))
    
    # calculate CRC
    crcini     = 0xffff
    crc        = crcini
    for c in frame:
        tmp    = crc^(ord(c))
        crc    = (crc>> 8)^hdlc.FCS16TAB[(tmp & 0xff)]
        log.debug("after {0}, crc={1}".format(hex(ord(c)),hex(crc)))

def test_randdomBackAndForth():
    
    log.debug("\n---------- test_randdomBackAndForth")
    
    hdlc = openhdlc.OpenHdlc()
    
    for frameLen in range(1,20):
        for run in range(10):
            # prepare random frame
            frame = []
            for _ in range(frameLen):
                frame += [random.randint(0x00,0xff)]
            frame = ''.join([chr(b) for b in frame])
            
            log.debug("frame:          {0}".format(u.formatBuf(frame)))
            
            # hdlcify
            frameHdlcified = hdlc.hdlcify(frame)
            log.debug("hdlcified:   {0}".format(u.formatBuf(frameHdlcified)))
            
            # dehdlcify
            frameDehdlcified = hdlc.dehdlcify(frameHdlcified)
            log.debug("dehdlcified:    {0}".format(u.formatBuf(frameDehdlcified)))
            
            assert frameDehdlcified==frame

