#!/usr/bin/python

import BspModule

class BspEui64(BspModule.BspModule):
    '''
    \brief Emulates the 'eui64' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspEui64')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_get(self):
        
        # log the activity
        self.log.debug('cmd_get')
        
        raise NotImplementedError()
    
    #======================== private =========================================