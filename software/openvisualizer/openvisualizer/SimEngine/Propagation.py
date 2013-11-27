#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging
import threading
import copy
import random

from openvisualizer.eventBus      import eventBusClient

import SimEngine

class Propagation(eventBusClient.eventBusClient):
    '''
    The propagation model of the engine.
    '''
    
    SIGNAL_WIRELESSTXSTART        = 'wirelessTxStart'
    SIGNAL_WIRELESSTXEND          = 'wirelessTxEnd'
    
    def __init__(self):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        
        # local variables
        self.dataLock             = threading.Lock()
        self.connections          = {}
        self.pendingTxEnd         = []
        
        # logging
        self.log                  = logging.getLogger('Propagation')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
        
        # initialize parents class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'Propagation',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : self.SIGNAL_WIRELESSTXSTART,
                    'callback'    : self._indicateTxStart,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : self.SIGNAL_WIRELESSTXEND,
                    'callback'    : self._indicateTxEnd,
                },
            ]
        )
        
    #======================== public ==========================================
    
    def createConnection(self,fromMote,toMote):
        
        pdr = random.random()
        pdr = 1.0
        
        with self.dataLock:
            
            # verify doesn't exist
            
            try:
                self.connections[fromMote][toMote]
            except KeyError:
                exists = False
            else:
                exists = True
            assert exists==False
            
            try:
                self.connections[toMote][fromMote]
            except KeyError:
                exists = False
            else:
                exists = True
            assert exists==False
            
            # create connection
            
            if fromMote not in self.connections:
                self.connections[fromMote] = {}
            self.connections[fromMote][toMote] = pdr
            
            if toMote not in self.connections:
                self.connections[toMote] = {}
            self.connections[toMote][fromMote] = pdr
    
    def retrieveConnections(self):
        
        retrievedConnections = []
        returnVal            = []
        with self.dataLock:
            
            for fromMote in self.connections:
                for toMote in self.connections[fromMote]:
                    if (toMote,fromMote) not in retrievedConnections:
                        returnVal += [
                            {
                                'fromMote': fromMote,
                                'toMote':   toMote,
                                'pdr':      self.connections[fromMote][toMote],
                            }
                        ]
                        retrievedConnections += [(fromMote,toMote)]
        
        return returnVal
    
    def updateConnection(self,fromMote,toMote,pdr):
        
        with self.dataLock:
            self.connections[fromMote][toMote] = pdr
            self.connections[toMote][fromMote] = pdr
    
    def deleteConnection(self,fromMote,toMote):
        
        with self.dataLock:
            
            # verify exists
            
            try:
                self.connections[fromMote][toMote]
            except KeyError:
                exists = False
            else:
                exists = True
            assert exists==True
            
            try:
                self.connections[toMote][fromMote]
            except KeyError:
                exists = False
            else:
                exists = True
            assert exists==True
            
            # remove connection
            del self.connections[fromMote][toMote]
            if not self.connections[fromMote]:
                del self.connections[fromMote]
            
            del self.connections[toMote][fromMote]
            if not self.connections[toMote]:
                del self.connections[toMote]
            
    
    #======================== indication from eventBus ========================
    
    def _indicateTxStart(self,sender,signal,data):
        
        (fromMote,packet,channel) = data
        
        if fromMote in self.connections:
            for (toMote,pdr) in self.connections[fromMote].items():
                if random.random()<=pdr:
                    
                    # indicate start of transmission
                    mh = self.engine.getMoteHandlerById(toMote)
                    mh.bspRadio.indicateTxStart(fromMote,packet,channel)
                    
                    # remember to signal end of transmission
                    self.pendingTxEnd += [(fromMote,toMote)]
    
    def _indicateTxEnd(self,sender,signal,data):
        
        fromMote = data
        
        if fromMote in self.connections:
            for (toMote,pdr) in self.connections[fromMote].items():
                try:
                    self.pendingTxEnd.remove((fromMote,toMote))
                except ValueError:
                    pass
                else:
                    mh = self.engine.getMoteHandlerById(toMote)
                    mh.bspRadio.indicateTxEnd(fromMote)
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    