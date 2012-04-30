#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class BspRadio(object):
    '''
    \brief Emulates the 'radio' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # logging
        self.log   = logging.getLogger('BspRadio')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    #======================== private =========================================