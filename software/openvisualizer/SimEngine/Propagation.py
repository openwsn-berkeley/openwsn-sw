#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass
    
class Propagation(object):
    '''
    \brief The propagation model of the engine.
    '''
    
    def __init__(self,engine):
        
        # store params
        self.engine               = engine
        
        # local variables
        
        # logging
        self.log                  = logging.getLogger('Propagation')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    