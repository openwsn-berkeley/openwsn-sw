#!/usr/bin/python

import BspModule

class BspBoard(BspModule.BspModule):
    '''
    \brief Emulates the 'board' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBoard')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_sleep(self):
        
        # log the activity
        self.log.debug('cmd_sleep')
    
    #======================== private =========================================