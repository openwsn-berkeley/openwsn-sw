#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class BspUart(object):
    '''
    \brief Emulates the 'uart' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # logging
        self.log   = logging.getLogger('BspUart')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================