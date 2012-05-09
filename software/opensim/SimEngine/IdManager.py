#!/usr/bin/python

import logging

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass
    
class IdManager(object):
    '''
    \brief The module which assigns ID to the motes.
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.currentId = 0
        
        # logging
        self.log                  = logging.getLogger('IdManager')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
    
    #======================== public ==========================================
    
    def getId(self):
        
        # increment the running ID
        self.currentId += 1
        
        # debug
        self.log.debug('assigning ID='+str(self.currentId))
        
        return self.currentId
    
    #======================== private =========================================
    
    #======================== helpers =========================================
    