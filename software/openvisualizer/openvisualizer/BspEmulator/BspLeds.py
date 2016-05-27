#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine   import SimEngine
import BspModule

class BspLeds(BspModule.BspModule):
    '''
    Emulates the 'leds' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.motehandler     = motehandler
        
        # local variables
        self.errorLedOn      = False
        self.radioLedOn      = False
        self.syncLedOn       = False
        self.debugLedOn      = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspLeds')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void leds_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
    
    # error LED
    
    def cmd_error_on(self):
        '''emulates
           void leds_error_on()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_error_on')
        
        # change the internal state
        self.errorLedOn = True
    
    def cmd_error_off(self):
        '''emulates
           void leds_error_off()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_error_off')
        
        # change the internal state
        self.errorLedOn = False
    
    def cmd_error_toggle(self):
        '''emulates
           void leds_error_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_error_toggle')
        
        # change the internal state
        self.errorLedOn = not self.errorLedOn
    
    def cmd_error_isOn(self):
        '''emulates
           uint8_t leds_error_isOn()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_error_isOn')
        
        if self.errorLedOn:
            returnVal = 1
        else:
            returnVal = 0
        
        return returnVal
    
    # radio LED
    
    def cmd_radio_on(self):
        '''emulates
           void leds_radio_on()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_on')
        
        # change the internal state
        self.radioLedOn = True
    
    def cmd_radio_off(self):
        '''emulates
           void leds_radio_off()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_off')
        
        # change the internal state
        self.radioLedOn = False
    
    def cmd_radio_toggle(self):
        '''emulates
           void leds_radio_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioLedOn = not self.radioLedOn
    
    def cmd_radio_isOn(self):
        '''emulates
           uint8_t leds_radio_isOn()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_isOn')
        
        if self.radioLedOn:
            returnVal = 1
        else:
            returnVal = 0
        
        return returnVal
    
    # sync LED
    
    def cmd_sync_on(self):
        '''emulates
           void leds_sync_on()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_sync_on')
        
        # change the internal state
        self.syncLedOn = True
    
    def cmd_sync_off(self):
        '''emulates
           void leds_sync_off()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_sync_off')
        
        # change the internal state
        self.syncLedOn = False
    
    def cmd_sync_toggle(self):
        '''emulates
           void leds_sync_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_sync_toggle')
        
        # change the internal state
        self.syncLedOn = not self.syncLedOn
    
    def cmd_sync_isOn(self):
        '''emulates
           uint8_t leds_sync_isOn()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_sync_isOn')
        
        if self.syncLedOn:
            returnVal = 1
        else:
            returnVal = 0
        
        return returnVal
    
    # debug LED
    
    def cmd_debug_on(self):
        '''emulates
           void leds_debug_on()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_debug_on')
        
        # change the internal state
        self.debugLedOn = True
    
    def cmd_debug_off(self):
        '''emulates
           void leds_debug_off()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_debug_off')
        
        # change the internal state
        self.debugLedOn = False
    
    def cmd_debug_toggle(self):
        '''emulates
           void leds_debug_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_debug_toggle')
        
        # change the internal state
        self.debugLedOn = not self.debugLedOn
    
    def cmd_debug_isOn(self):
        '''emulates
           uint8_t leds_debug_isOn()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_debug_isOn')
        
        if self.debugLedOn:
            returnVal = 1
        else:
            returnVal = 0
        
        return returnVal
    
    # all LEDs
    
    def cmd_all_on(self):
        '''emulates'
           void leds_all_on()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_all_on')
        
        # change the internal state
        self.errorLedOn      = True
        self.radioLedOn      = True
        self.syncLedOn       = True
        self.debugLedOn      = True
    
    def cmd_all_off(self):
        '''emulates
           void leds_all_off()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_all_off')
        
        # change the internal state
        self.errorLedOn      = False
        self.radioLedOn      = False
        self.syncLedOn       = False
        self.debugLedOn      = False
    
    def cmd_all_toggle(self):
        '''emulates
           void leds_all_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_all_toggle')
        
        # change the internal state
        self.errorLedOn      = not self.errorLedOn
        self.radioLedOn      = not self.radioLedOn
        self.syncLedOn       = not self.syncLedOn
        self.debugLedOn      = not self.debugLedOn
    
    def cmd_circular_shift(self):
        '''emulates
           void leds_circular_shift()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_circular_shift')
        
        (self.errorLedOn,
         self.radioLedOn,
         self.syncLedOn,
         self.debugLedOn) = (self.radioLedOn,
                             self.syncLedOn,
                             self.debugLedOn,
                             self.errorLedOn)
    
    def cmd_increment(self):
        '''emulates
           void leds_increment()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_increment')
        
        # get the current value
        val  = 0
        if self.errorLedOn:
            val += 0x08
        if self.radioLedOn:
            val += 0x04
        if self.syncLedOn:
            val += 0x02
        if self.debugLedOn:
            val += 0x01
        
        # increment
        val = (val+1)%0xf
        
        # apply back
        self.errorLedOn = ((val & 0x08)!=0)
        self.radioLedOn = ((val & 0x04)!=0)
        self.syncLedOn  = ((val & 0x02)!=0)
        self.debugLedOn = ((val & 0x01)!=0)
    
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