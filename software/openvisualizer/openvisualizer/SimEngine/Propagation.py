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
        self.connections          = []
        
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
        
        with self.dataLock:
        
            exists = False
            
            for connection in self.connections:
                if (connection['fromMote']==fromMote and connection['toMote']==toMote):
                    exists = True
            
            if not exists:
                self.connections += [
                    {
                        'fromMote':   fromMote,
                        'toMote':     toMote,
                        'pdr':        random.random(),
                    }
                ]
    
    def retrieveConnections(self):
        
        with self.dataLock:
            return copy.deepcopy(self.connections)
    
    def updateConnection(self,fromMote,toMote,pdr):
        
        with self.dataLock:
            
            found = False
            
            for connection in self.connections:
                if (connection['fromMote']==fromMote and connection['toMote']==toMote):
                    connection['pdr']=pdr
                    found = True
            
            assert found==True
    
    def deleteConnection(self,fromMote,toMote):
        
        with self.dataLock:
            
            exists = False
            
            for i in range(len(self.connections)):
                if (self.connections[i]['fromMote']==fromMote and self.connections[i]['toMote']==toMote):
                    exists = True
                    self.connections.pop(i)
                    break
            
            assert exists==True
    
    #======================== indication from eventBus ========================
    
    def _indicateTxStart(self,sender,signal,data):
        
        (moteId,packet,channel) = data
        
        for mh in self.engine.moteHandlers:
            mh.bspRadio.indicateTxStart(moteId,packet,channel)
    
    def _indicateTxEnd(self,sender,signal,data):
        
        moteId = data
        
        for mh in self.engine.moteHandlers:
            mh.bspRadio.indicateTxEnd(moteId)
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    