#!/usr/bin/python

import threading
import logging
import random
import time
import os
import subprocess

from DaemonThread import DaemonThread
from SimCli       import SimCli

PATH_TO_BIN = os.path.join('..','..','..','..','firmware','openos','projects','common')
BIN_BSP_LEDS = os.path.join(PATH_TO_BIN,'01bsp_leds','bsp_leds')

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class SimEngine(object):
    '''
    \brief The main simulation engine.
    '''
    
    TCPPORT            = 14159
    
    def __init__(self,nummotes=1,motebin=BIN_BSP_LEDS):
        
        # store params
        self.nummotes             = nummotes
        self.motebin              = motebin
        
        # local variables
        self.moteHandlers         = []
        self.pauseSem             = threading.Lock()
        self.isPaused             = False
        self.delay              = 0
        
        # logging
        self.log                  = logging.getLogger('SimEngine')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # create daemon thread to handle connection of newly created motes
        self.daemonThreadHandler  = DaemonThread(self,self.TCPPORT)
        self.cliHandler           = SimCli(self)
    
    def start(self):
        
        # log
        self.log.info('starting')
        
        # start daemon thread (ready to accept connections)
        self.daemonThreadHandler.start()
        
        # start motes
        for i in range(self.nummotes):
            subprocess.Popen(self.motebin)
        
        # start CLI threads
        self.cliHandler.start()
    
    #======================== public ==========================================
    
    def setDelay(self,delay):
        self.delay = delay
    
    def pause(self):
        if not self.isPaused:
            self.pauseSem.acquire()
            self.isPaused = True
    
    def resume(self):
        if self.isPaused:
            self.pauseSem.release()
            self.isPaused = False
    
    def pauseOrDelay(self):
        if self.isPaused:
            self.pauseSem.acquire()
            self.pauseSem.release()
        else:
            time.sleep(self.delay)
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    