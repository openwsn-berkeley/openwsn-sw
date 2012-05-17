#!/usr/bin/python

import BspModule

class BspEui64(BspModule.BspModule):
    '''
    \brief Emulates the 'eui64' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspEui64')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_get(self,params):
        '''emulates
           void eui64_get(uint8_t* addressToWrite)'''
        
        # log the activity
        self.log.debug('cmd_get')
        
        # get my 16-bit ID
        myId    = self.motehandler.getId()
        
        # format my EUI64
        myEui64 = [0x14,015,0x92,0xcc,0x00,0x00,((myId>>8) & 0xff),
                                                ((myId>>0) & 0xff)]
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_eui64_get'],
                                     myEui64)
    
    #======================== private =========================================