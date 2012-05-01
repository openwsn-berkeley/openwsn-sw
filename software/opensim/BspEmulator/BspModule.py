#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class BspModule(object):
    '''
    \brief Emulates the 'board' BSP module
    '''
    
    def __init__(self,name):
        
        # store params
        
        # local variables
        self.isInitialized = False
        
        # logging
        self.log   = logging.getLogger(name)
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
    
    #=== getters
    
    def getIsInitialized():
       return self.isInitialized
    
    #======================== private =========================================
    
    def _checkInit(self):
        assert(self.isInitialized)
    