#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class BspBoard(object):
    '''
    \brief Emulates the 'board' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # logging
        self.log   = logging.getLogger('BspBoard')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
    
    #======================== public ==========================================
    
    def init(self):
        print 'TODO'
    
    def sleep(self):
        print 'TODO'
    
    #======================== private =========================================