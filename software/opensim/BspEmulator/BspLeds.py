#!/usr/bin/python

import BspModule

class BspLeds(BspModule.BspModule):
    '''
    \brief Emulates the 'leds' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspLeds')
    
    #======================== public ==========================================
    
    #=== commands
        
    def cmd_error_on(self):
        
        # log the activity
        self.log.debug('cmd_error_on')
        
        raise NotImplementedError()
        
    def cmd_error_off(self):
        
        # log the activity
        self.log.debug('cmd_error_off')
        
        raise NotImplementedError()
        
    def cmd_error_toggle(self):
        
        # log the activity
        self.log.debug('cmd_error_toggle')
        
        raise NotImplementedError()
        
    def cmd_error_isOn(self):
        
        # log the activity
        self.log.debug('cmd_error_isOn')
        
        raise NotImplementedError()
        
    def cmd_radio_on(self):
        
        # log the activity
        self.log.debug('cmd_radio_on')
        
        raise NotImplementedError()
        
    def cmd_radio_off(self):
        
        # log the activity
        self.log.debug('cmd_radio_off')
        
        raise NotImplementedError()
        
    def cmd_radio_toggle(self):
        
        # log the activity
        self.log.debug('cmd_radio_toggle')
        
        raise NotImplementedError()
        
    def cmd_radio_isOn(self):
        
        # log the activity
        self.log.debug('cmd_radio_isOn')
        
        raise NotImplementedError()
        
    def cmd_sync_on(self):
        
        # log the activity
        self.log.debug('cmd_sync_on')
        
        raise NotImplementedError()
        
    def cmd_sync_off(self):
        
        # log the activity
        self.log.debug('cmd_sync_off')
        
        raise NotImplementedError()
        
    def cmd_sync_toggle(self):
        
        # log the activity
        self.log.debug('cmd_sync_toggle')
        
        raise NotImplementedError()
        
    def cmd_sync_isOn(self):
        
        # log the activity
        self.log.debug('cmd_sync_isOn')
        
        raise NotImplementedError()
        
    def cmd_debug_on(self):
        
        # log the activity
        self.log.debug('cmd_debug_on')
        
        raise NotImplementedError()
        
    def cmd_debug_off(self):
        
        # log the activity
        self.log.debug('cmd_debug_off')
        
        raise NotImplementedError()
        
    def cmd_debug_toggle(self):
        
        # log the activity
        self.log.debug('cmd_debug_toggle')
        
        raise NotImplementedError()
        
    def cmd_debug_isOn(self):
        
        # log the activity
        self.log.debug('cmd_debug_isOn')
        
        raise NotImplementedError()
        
    def cmd_all_on(self):
        
        # log the activity
        self.log.debug('cmd_all_on')
        
        raise NotImplementedError()
        
    def cmd_all_off(self):
        
        # log the activity
        self.log.debug('cmd_all_off')
        
        raise NotImplementedError()
        
    def cmd_all_toggle(self):
        
        # log the activity
        self.log.debug('cmd_all_toggle')
        
        raise NotImplementedError()
        
    def cmd_circular_shift(self):
        
        # log the activity
        self.log.debug('cmd_circular_shift')
        
        raise NotImplementedError()
        
    def cmd_increment(self):
        
        # log the activity
        self.log.debug('cmd_increment')
        
        raise NotImplementedError()
    
    #======================== private =========================================