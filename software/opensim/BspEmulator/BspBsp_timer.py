#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class BspBsp_timer(object):
    '''
    \brief Emulates the 'bsp_timer' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # logging
        self.log   = logging.getLogger('BspBsp_timer')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================