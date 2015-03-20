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
from math import radians, cos, sin, asin, sqrt, log10

from openvisualizer.eventBus      import eventBusClient

import SimEngine

class Propagation(eventBusClient.eventBusClient):
    '''
    The propagation model of the engine.
    '''
    
    SIGNAL_WIRELESSTXSTART        = 'wirelessTxStart'
    SIGNAL_WIRELESSTXEND          = 'wirelessTxEnd'
    
    def __init__(self,simTopology):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        self.simTopology          = simTopology
        
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
  
        
        FREQUENCY_GHz        =    2.4
        TX_POWER_dBm         =    0.0
        PISTER_HACK_LOSS     =   40.0
        SENSITIVITY_dBm      = -101.0
        GREY_AREA_dB         =   15.0
        
        with self.dataLock:
            
            if not self.simTopology:
                
                #===== Pister-hack model
                
                # retrieve position
                mhFrom            = self.engine.getMoteHandlerById(fromMote)
                (latFrom,lonFrom) = mhFrom.getLocation()
                mhTo              = self.engine.getMoteHandlerById(toMote)
                (latTo,lonTo)     = mhTo.getLocation()
    
                # compute distance
                lonFrom, latFrom, lonTo, latTo = map(radians, [lonFrom, latFrom, lonTo, latTo])
                dlon             = lonTo - lonFrom 
                dlat             = latTo - latFrom 
                a                = sin(dlat/2)**2 + cos(latFrom) * cos(latTo) * sin(dlon/2)**2
                c                = 2 * asin(sqrt(a)) 
                d_km                = 6367 * c
                
                # compute reception power (first Friis, then apply Pister-hack)
                Prx              = TX_POWER_dBm - (20*log10(d_km) + 20*log10(FREQUENCY_GHz) + 92.45)
                Prx             -= PISTER_HACK_LOSS*random.random()
               
                #turn into PDR
                if   Prx<SENSITIVITY_dBm:
                    pdr          = 0.0
                elif Prx>SENSITIVITY_dBm+GREY_AREA_dB:
                    pdr          = 1.0
                else:
                    pdr          = (Prx-SENSITIVITY_dBm)/GREY_AREA_dB

            elif self.simTopology=='linear':
                
                # linear network
                if fromMote==toMote+1:
                    pdr          = 1.0
                else:
                    pdr          = 0.0
            
            elif self.simTopology=='fully-meshed':
                
                pdr          = 1.0
            
            else:
                
                raise NotImplementedError('unsupported simTopology={0}'.format(self.simTopology))
            
            #==== create, update or delete connection
            
            if pdr:
                if fromMote not in self.connections:
                    self.connections[fromMote] = {}
                self.connections[fromMote][toMote] = pdr
                
                if toMote not in self.connections:
                    self.connections[toMote] = {}
                self.connections[toMote][fromMote] = pdr
            else:
                self.deleteConnection(toMote,fromMote)
    
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
            
            try:
                del self.connections[fromMote][toMote]
                if not self.connections[fromMote]:
                    del self.connections[fromMote]
                
                del self.connections[toMote][fromMote]
                if not self.connections[toMote]:
                    del self.connections[toMote]
            except KeyError:
                pass # did not exist
    
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
    
