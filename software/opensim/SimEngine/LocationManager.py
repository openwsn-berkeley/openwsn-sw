#!/usr/bin/python

import random
import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass
    
class LocationManager(object):
    '''
    \brief The module which assigns locations to the motes.
    '''
    
    def __init__(self,engine):
        
        # store params
        self.engine               = engine
        
        # local variables
        
        # logging
        self.log                  = logging.getLogger('LocationManager')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
    
    #======================== public ==========================================
    
    def getLocation(self):
        
        x = random.randint(0,100)
        y = random.randint(0,100)
        z = 0
        
        # debug
        self.log.debug('assigning location ('+str(x)+','+str(y)+','+str(z)+')')
        
        return (x,y,z)
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    