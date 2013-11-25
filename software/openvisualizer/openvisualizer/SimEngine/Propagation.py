#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging

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
    