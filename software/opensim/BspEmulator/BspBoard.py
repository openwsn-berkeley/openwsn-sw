#!/usr/bin/python

import BspModule

class BspBoard(BspModule.BspModule):
    '''
    \brief Emulates the 'board' BSP module
    '''
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine          = engine
        self.motehandler     = motehandler
        
        # local variables
        self.timeline        = self.engine.timeline
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspBoard')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        '''emulates:
           void board_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_board_init'])
    
    def cmd_sleep(self,params):
        '''emulates
           void board_init()'''
        
        # log the activity
        self.log.debug('cmd_sleep')
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # have the timeline advance to the next event
        self.timeline.nextEvent()
    
    #======================== private =========================================