#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import random
import logging
    
class LocationManager(object):
    '''
    The module which assigns locations to the motes.
    '''
    
    def __init__(self,engine):
        
        # store params
        self.engine               = engine
        
        # local variables
        
        # logging
        self.log                  = logging.getLogger('LocationManager')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
        
    
    #======================== public ==========================================
    
    def getLocation(self):
        
        x = random.randint(0,100)
        y = random.randint(0,100)
        z = 0
        
        # debug
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('assigning location ('+str(x)+','+str(y)+','+str(z)+')')
        
        return (x,y,z)
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    