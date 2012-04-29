#!/usr/bin/python

import threading
import logging
import random

from DaemonThread import DaemonThread
from SimCli       import SimCli

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class SimEngine(object):
    '''
    \brief The main simulation engine.
    '''
    
    TCPPORT            = 14159
    
    def __init__(self,nummotes):
        
        # store params
        self.nummotes             = nummotes
        
        # local variables
        self.moteHandlers         = []
        
        # logging
        self.log                  = logging.getLogger('SimEngine')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # create daemon thread to handle connection of newly created motes
        self.daemonThreadHandler  = DaemonThread(self.TCPPORT)
        self.cliHandler           = SimCli()
    
    def start(self):
        
        # log
        self.log.info('starting')
        
        # start threads
        self.daemonThreadHandler.start()
        self.cliHandler.start()
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    