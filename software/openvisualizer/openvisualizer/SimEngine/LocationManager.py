#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import random
import logging

import SimEngine

class LocationManager(object):
    '''
    The module which assigns locations to the motes.
    '''
    
    def __init__(self):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        
        # local variables
        
        # logging
        self.log                  = logging.getLogger('LocationManager')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(logging.NullHandler())
    
    #======================== public ==========================================
    
    def getLocation(self):
        
        # get random location around Cory Hall, UC Berkeley
        lat =   37.875095-0.0005+random.random()*0.0010
        lon = -122.257473-0.0005+random.random()*0.0010
        
        # debug
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('assigning location ({0} {1})'.format(lat,lon))
        
        return lat, lon
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    