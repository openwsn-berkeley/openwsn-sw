#!/usr/bin/python

import os
import sys

temp_path = sys.path[0]
if temp_path:
    sys.path.insert(0, os.path.join(temp_path, '..', '..'))

import logging
import logging.handlers
import binascii
from SimEngine import SimEngine
from SimCli    import SimCli

LOG_FORMAT  = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"

#============================ logging =========================================

logFileName = 'logs/opensim.log'
loghandler  = logging.handlers.RotatingFileHandler(logFileName,
                                                   maxBytes=2000000,
                                                   backupCount=5,
                                                   mode='w')
loghandler.setFormatter(logging.Formatter(LOG_FORMAT))

#============================ main ============================================

def main():
    
    # instantiate a SimEngine object
    simengine        = SimEngine.SimEngine(loghandler)
    simengine.start()
    
    # instantiate the CLI interface
    cliHandler       = SimCli.SimCli(simengine)
    cliHandler.start()
            
if __name__ == "__main__":
    main()
