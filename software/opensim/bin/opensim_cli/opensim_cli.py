#!/usr/bin/python

import os
import sys

if __name__=='__main__':
    here = sys.path[0]
    # opensim/
    sys.path.insert(0, os.path.join(here, '..', '..'))
    # location of openwsn module
    sys.path.insert(0, os.path.join(here, '..', '..', '..', '..', '..', 'openwsn-fw', 'firmware','openos','projects','common'))

import logging
import logging.handlers
import binascii

from SimEngine import SimEngine, \
                      MoteHandler
from SimCli    import SimCli

import oos_openwsn

LOG_FORMAT  = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"

#============================ logging =========================================

logFileName = 'opensim.log'
loghandler  = logging.handlers.RotatingFileHandler(logFileName,
                                                   maxBytes=2000000,
                                                   backupCount=5,
                                                   mode='w')
loghandler.setFormatter(logging.Formatter(LOG_FORMAT))

#============================ main ============================================

def main():
    
    # instantiate a SimEngine object
    simengine        = SimEngine.SimEngine(loghandler)
    
    # instantiate the CLI interface
    cliHandler       = SimCli.SimCli(simengine)
    
    # start threads
    simengine.start()
    cliHandler.start()
    
    # add motes
    for _ in range(10):
        # create a mote
        moteHandler = MoteHandler.MoteHandler(simengine,oos_openwsn.OpenMote())
        
        # indicate to the engine that there is a new mote
        simengine.indicateNewMote(moteHandler)

if __name__ == "__main__":
    main()
