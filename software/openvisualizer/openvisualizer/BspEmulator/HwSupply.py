#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine     import SimEngine
import HwModule

class HwSupply(HwModule.HwModule):
    '''
    Emulates the mote's power supply
    '''
    
    INTR_SWITCHON  = 'hw_supply.switchOn'
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        self.moteOn = False
        
        # initialize the parent
        HwModule.HwModule.__init__(self,'HwSupply')
    
    #======================== public ==========================================
    
    def switchOn(self):
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('switchOn')
        
        # filter error
        if self.moteOn:
            raise RuntimeError('mote already on')
        
        # change local variable
        self.moteOn = True
        
        # have the crystal start now
        self.motehandler.hwCrystal.start()
        
        # send command to mote
        self.motehandler.mote.supply_on()
    
    def switchOff(self):
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('switchOff')
        
        # filter error
        if not self.moteOn:
            raise RuntimeError('mote already off')
        
        # change local variable
        self.moteOn = False
        
    def isOn(self):
        return self.moteOn
    
    #======================== private =========================================