#!/usr/bin/python

import random
import HwModule

class HwCrystal(HwModule.HwModule):
    '''
    \brief Emulates the mote's crystal.
    '''
    
    def __init__(self,frequency,maxDrift=0):
        
        # store params
        self.frequency = frequency
        self.maxDrift  = maxDrift
        
        # local variables
        self.drift     = float(random.uniform(-self.maxDrift,
                                              +self.maxDrift))
        
        # initialize the parent
        HwModule.HwModule.__init__(self,'HwCrystal')
    
    #======================== public ==========================================
    
    def getDuration(self,cycles):
        
        period     = float(1)/float(self.frequency)        # nominal period
        period    += self.drift*float(period/1000000)      # apply drift
        
        duration   = cycles*period
        
        self.log.debug(srt(cycles)+' cycles = '+str(duration*1000)+' ms')
        
        return duration
    
    #======================== private =========================================