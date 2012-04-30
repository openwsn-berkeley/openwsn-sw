#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class BspLeds(object):
    '''
    \brief Emulates the 'leds' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # logging
        self.log   = logging.getLogger('BspLeds')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================