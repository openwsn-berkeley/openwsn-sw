#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class HwModule(object):
    '''
    \brief Parent class for all hardware modules.
    '''
    
    def __init__(self,name):
        
        # store params
        
        # local variables
        self.isInitialized = False
        
        # logging
        self.log  = logging.getLogger(name+'_'+str(self.motehandler.getId()))
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================
    