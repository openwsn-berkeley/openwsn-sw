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
    
    def cmd_init(self,params):
        '''emulates
           void leds_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_init'])
        
    def cmd_error_on(self,params):
        '''emulates
           void leds_error_on()'''
        
        # log the activity
        self.log.debug('cmd_error_on')
        
        # change the internal state
        self.errorLedOn = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_error_on'])
        
    def cmd_error_off(self,params):
        '''emulates
           void leds_error_off()'''
        
        # log the activity
        self.log.debug('cmd_error_off')
        
        # change the internal state
        self.errorLedOn = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_error_off'])
        
    def cmd_error_toggle(self,params):
        '''emulates
           void leds_error_toggle()'''
        
        # log the activity
        self.log.debug('cmd_error_toggle')
        
        # change the internal state
        self.errorLedOn = not self.errorLedOn
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_error_toggle'])
        
    def cmd_error_isOn(self,params):
        '''emulates
           uint8_t leds_error_isOn()'''
        
        # log the activity
        self.log.debug('cmd_error_isOn')
        
        raise NotImplementedError()
        
    def cmd_radio_on(self,params):
        '''emulates
           void leds_radio_on()'''
        
        # log the activity
        self.log.debug('cmd_radio_on')
        
        # change the internal state
        self.radioLedOn = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_radio_on'])
        
    def cmd_radio_off(self,params):
        '''emulates
           void leds_radio_off()'''
        
        # log the activity
        self.log.debug('cmd_radio_off')
        
        # change the internal state
        self.radioLedOn = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_radio_off'])
        
    def cmd_radio_toggle(self,params):
        '''emulates
           void leds_radio_toggle()'''
        
        # log the activity
        self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioLedOn = not self.radioLedOn
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_radio_toggle'])
        
    def cmd_radio_isOn(self,params):
        '''emulates
           uint8_t leds_radio_isOn()'''
        
        # log the activity
        self.log.debug('cmd_radio_isOn')
        
        raise NotImplementedError()
        
    def cmd_sync_on(self,params):
        '''emulates
           void leds_sync_on()'''
        
        # log the activity
        self.log.debug('cmd_sync_on')
        
        # change the internal state
        self.syncLedOn = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_sync_on'])
        
    def cmd_sync_off(self,params):
        '''emulates
           void leds_sync_off()'''
        
        # log the activity
        self.log.debug('cmd_sync_off')
        
        # change the internal state
        self.syncLedOn = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_sync_off'])
        
    def cmd_sync_toggle(self,params):
        '''emulates
           void leds_sync_toggle()'''
        
        # log the activity
        self.log.debug('cmd_sync_toggle')
        
        # change the internal state
        self.syncLedOn = not self.syncLedOn
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_sync_toggle'])
        
    def cmd_sync_isOn(self,params):
        '''emulates
           uint8_t leds_sync_isOn()'''
        
        # log the activity
        self.log.debug('cmd_sync_isOn')
        
        raise NotImplementedError()
        
    def cmd_debug_on(self,params):
        '''emulates
           void leds_debug_on()'''
        
        # log the activity
        self.log.debug('cmd_debug_on')
        
        # change the internal state
        self.debugLedOn = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_debug_on'])
        
    def cmd_debug_off(self,params):
        '''emulates
           void leds_debug_off()'''
        
        # log the activity
        self.log.debug('cmd_debug_off')
        
        # change the internal state
        self.debugLedOn = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_debug_off'])
        
    def cmd_debug_toggle(self,params):
        '''emulates
           void leds_debug_toggle()'''
        
        # log the activity
        self.log.debug('cmd_debug_toggle')
        
        # change the internal state
        self.debugLedOn = not self.debugLedOn
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_debug_toggle'])
        
    def cmd_debug_isOn(self,params):
        '''emulates
           uint8_t leds_debug_isOn()'''
        
        # log the activity
        self.log.debug('cmd_debug_isOn')
        
        raise NotImplementedError()
        
    def cmd_all_on(self,params):
        '''emulates'
           void leds_all_on()'''
        
        # log the activity
        self.log.debug('cmd_all_on')
        
        # change the internal state
        self.errorLedOn      = True
        self.radioLedOn      = True
        self.syncLedOn       = True
        self.debugLedOn      = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_all_on'])
        
    def cmd_all_off(self,params):
        '''emulates
           void leds_all_off()'''
        
        # log the activity
        self.log.debug('cmd_all_off')
        
        # change the internal state
        self.errorLedOn      = False
        self.radioLedOn      = False
        self.syncLedOn       = False
        self.debugLedOn      = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_all_off'])
        
    def cmd_all_toggle(self,params):
        '''emulates
           void leds_all_toggle()'''
        
        # log the activity
        self.log.debug('cmd_all_toggle')
        
        # change the internal state
        self.errorLedOn      = not self.errorLedOn
        self.radioLedOn      = not self.radioLedOn
        self.syncLedOn       = not self.syncLedOn
        self.debugLedOn      = not self.debugLedOn
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_all_toggle'])
        
    def cmd_circular_shift(self,params):
        '''emulates
           void leds_circular_shift()'''
        
        # log the activity
        self.log.debug('cmd_circular_shift')
        
        (self.errorLedOn, \
         self.radioLedOn, \
         self.syncLedOn,  \
         self.debugLedOn) = (self.radioLedOn, \
                             self.syncLedOn,  \
                             self.debugLedOn, \
                             self.errorLedOn)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_circular_shift'])
        
    def cmd_increment(self,params):
        '''emulates
           void leds_increment()'''
        
        # log the activity
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
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_leds_increment'])
    
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