#!/usr/bin/python

import BspModule

class BspLeds(BspModule.BspModule):
    '''
    \brief Emulates the 'leds' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        self.errorLedOn      = False
        self.radioLedOn      = False
        self.syncLedOn       = False
        self.debugLedOn      = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspLeds')
    
    #======================== public ==========================================
    
    #=== commands
        
    def cmd_error_on(self,params):
        
        # log the activity
        self.log.debug('cmd_error_on')
        
        # change the internal state
        self.errorLedOn = True
        
    def cmd_error_off(self,params):
        
        # log the activity
        self.log.debug('cmd_error_off')
        
        # change the internal state
        self.errorLedOn = False
        
    def cmd_error_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_error_toggle')
        
        # change the internal state
        self.errorLedOn = not self.errorLedOn
        
    def cmd_error_isOn(self,params):
        
        # log the activity
        self.log.debug('cmd_error_isOn')
        
        raise NotImplementedError()
        
    def cmd_radio_on(self,params):
        
        # log the activity
        self.log.debug('cmd_radio_on')
        
        # change the internal state
        self.radioLedOn = True
        
    def cmd_radio_off(self,params):
        
        # log the activity
        self.log.debug('cmd_radio_off')
        
        # change the internal state
        self.radioLedOn = False
        
    def cmd_radio_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioLedOn = not self.radioLedOn
        
    def cmd_radio_isOn(self,params):
        
        # log the activity
        self.log.debug('cmd_radio_isOn')
        
        raise NotImplementedError()
        
    def cmd_sync_on(self,params):
        
        # log the activity
        self.log.debug('cmd_sync_on')
        
        # change the internal state
        self.syncLedOn = True
        
    def cmd_sync_off(self,params):
        
        # log the activity
        self.log.debug('cmd_sync_off')
        
        # change the internal state
        self.syncLedOn = False
        
    def cmd_sync_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_sync_toggle')
        
        # change the internal state
        self.syncLedOn = not self.syncLedOn
        
    def cmd_sync_isOn(self,params):
        
        # log the activity
        self.log.debug('cmd_sync_isOn')
        
        raise NotImplementedError()
        
    def cmd_debug_on(self,params):
        
        # log the activity
        self.log.debug('cmd_debug_on')
        
        # change the internal state
        self.debugLedOn = True
        
    def cmd_debug_off(self,params):
        
        # log the activity
        self.log.debug('cmd_debug_off')
        
        # change the internal state
        self.debugLedOn = False
        
    def cmd_debug_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_debug_toggle')
        
        # change the internal state
        self.debugLedOn = not self.debugLedOn
        
    def cmd_debug_isOn(self,params):
        
        # log the activity
        self.log.debug('cmd_debug_isOn')
        
        raise NotImplementedError()
        
    def cmd_all_on(self,params):
        
        # log the activity
        self.log.debug('cmd_all_on')
        
        # change the internal state
        self.errorLedOn      = True
        self.radioLedOn      = True
        self.syncLedOn       = True
        self.debugLedOn      = True
        
    def cmd_all_off(self,params):
        
        # log the activity
        self.log.debug('cmd_all_off')
        
        # change the internal state
        self.errorLedOn      = False
        self.radioLedOn      = False
        self.syncLedOn       = False
        self.debugLedOn      = False
        
    def cmd_all_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_all_toggle')
        
        # change the internal state
        self.errorLedOn      = not self.errorLedOn
        self.radioLedOn      = not self.radioLedOn
        self.syncLedOn       = not self.syncLedOn
        self.debugLedOn      = not self.debugLedOn
        
    def cmd_circular_shift(self,params):
        
        # log the activity
        self.log.debug('cmd_circular_shift')
        
        (self.errorLedOn, \
         self.radioLedOn, \
         self.syncLedOn,  \
         self.debugLedOn) = (self.radioLedOn, \
                             self.syncLedOn,  \
                             self.debugLedOn, \
                             self.errorLedOn)
        
    def cmd_increment(self,params):
        
        # log the activity
        self.log.debug('cmd_increment')
        
        # get the current value
        val  = 0
        rank = 1
        for i in [self.debugLedOn,self.syncLedOn,self.radioLedOn,self.errorLedOn]:
            if i:
                val  += pow(2,rank)
                rank += 1
        
        # increment
        val = (val+1)%16
        
        # apply back
        self.errorLedOn = (val & 1<<3)
        self.radioLedOn = (val & 1<<2)
        self.syncLedOn  = (val & 1<<1)
        self.debugLedOn = (val & 1<<0)
    
    #=== getters
    
    def get_errorLedOn(self):
        return self.errorLedOn
    
    def get_radioLedOn(self):
        return self.radioLedOn
    
    def get_syncLedOn(self):
        return self.syncLedOn
    
    def get_debugLedOn(self):
        return self.debugLedOn
    
    #======================== private =========================================