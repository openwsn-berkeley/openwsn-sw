#!/usr/bin/python

import BspModule

class BspBoard(BspModule.BspModule):
    '''
    \brief Emulates the 'board' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBoard')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_sleep(self,params):
        
        # log the activity
        self.log.debug('cmd_sleep')
    
    #======================== private =========================================