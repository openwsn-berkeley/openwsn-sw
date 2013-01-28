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

def test_randdomBackAndForth():
    
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
