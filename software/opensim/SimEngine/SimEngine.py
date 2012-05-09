#!/usr/bin/python

import threading
import logging
import random
import time
import os
import subprocess

import TimeLine
import Propagation
import IdManager
import LocationManager
import DaemonThread
import SimCli

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
        self.timeline             = TimeLine.TimeLine()
        self.propagation          = Propagation.Propagation()
        self.idmanager            = IdManager.IdManager()
        self.locationmanager      = LocationManager.LocationManager() 
        self.pauseSem             = threading.Lock()
        self.isPaused             = False
        self.stopAfterSteps       = None
        self.delay                = 0
        
        # logging
        self.log                  = logging.getLogger('SimEngine')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # create daemon thread to handle connection of newly created motes
        self.daemonThreadHandler  = DaemonThread.DaemonThread(self,self.TCPPORT)
        self.cliHandler           = SimCli.SimCli(self)
    
    def start(self):
        
        # log
        self.log.info('starting')
        
        # start daemon thread (ready to accept connections)
        self.daemonThreadHandler.start()
        
        # start motes
        '''
        for i in range(self.nummotes):
            subprocess.Popen(self.motebin)
        '''
        
        # start CLI threads
        self.cliHandler.start()
    
    #======================== public ==========================================
    
    #=== controlling execution speed
    
    def setDelay(self,delay):
        self.delay = delay
    
    def pause(self):
        if not self.isPaused:
            self.pauseSem.acquire()
            self.isPaused = True
    
    def step(self,numSteps):
        self.stopAfterSteps = numSteps
        if self.isPaused:
            self.pauseSem.release()
            self.isPaused = False
    
    def resume(self):
        self.stopAfterSteps = None
        if self.isPaused:
            self.pauseSem.release()
            self.isPaused = False
    
    def pauseOrDelay(self):
        if self.isPaused:
            self.pauseSem.acquire()
            self.pauseSem.release()
        else:
            time.sleep(self.delay)
            
        if self.stopAfterSteps!=None:
            if self.stopAfterSteps>0:
                self.stopAfterSteps -= 1
            if self.stopAfterSteps==0:
                self.pause()
        
        assert(self.stopAfterSteps==None or self.stopAfterSteps>=0)
    
    #=== called from the DaemonThread
    
    def indicateNewMote(self,moteHandler):
        
        # assign an ID to this mote
        moteHandler.setId(self.idmanager.getId())
        
        # assign a location to this mote
        moteHandler.setLocation(self.locationmanager.getLocation())
        
        # add this mote to my list of motes
        self.moteHandlers.append(moteHandler)
    
    #=== getting information about the system
    
    def getNumMotes(self):
        return len(self.moteHandlers)
    
    def getMoteHandler(self,rank):
        return self.moteHandlers[rank]
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    