#!/usr/bin/python

import BspModule

class BspSupply(BspModule.BspModule):
    '''
    \brief Emulates the mote's power supply
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.moteOn = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspSupply')
    
    #======================== public ==========================================
    
    def switchOn(self):
        
        # log the activity
        self.log.debug('switchOn')
        
        # filter error
        if self.moteOn:
            raise RuntimeError('mote already on')
        
        # change local variable
        self.moteOn = True
    
    def switchOff(self):
        
        # log the activity
        self.log.debug('switchOff')
        
        # filter error
        if not self.moteOn:
            raise RuntimeError('mote already off')
        
        # change local variable
        self.moteOn = False
        
    def isOn(self):
        return self.moteOn
    
    #======================== private =========================================