#!/usr/bin/python

import os
import sys

if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))
    sys.path.insert(0, os.path.join(here, '..', '..','..'))

import logging
import logging.handlers
import binascii
from SimEngine import SimEngine

from openUI    import SimGui
from openUI    import SimWindow

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
    simengine.start()
    
    # instantiate the CLI interface
    guiHandler       = SimGui.SimGui(simengine)
    guiHandler.start()
            
if __name__ == "__main__":
    main()
