#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

import BspModule

class BspDebugpins(BspModule.BspModule):
    '''
    Emulates the 'debugpins' BSP module
    '''
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine          = engine
        self.motehandler     = motehandler
        
        # local variables
        self.framePinHigh    = False
        self.slotPinHigh     = False
        self.fsmPinHigh      = False
        self.taskPinHigh     = False
        self.isrPinHigh      = False
        self.radioPinHigh    = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspDebugpins')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void debugpins_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
    
    def cmd_frame_toggle(self):
        '''emulates
           void debugpins_frame_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_frame_toggle')
        
        # change the internal state
        self.framePinHigh = not self.framePinHigh
    
    def cmd_frame_clr(self):
        '''emulates
           void debugpins_frame_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_frame_clr')
        
        # change the internal state
        self.framePinHigh = False
    
    def cmd_frame_set(self):
        '''emulates
           void debugpins_frame_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_frame_set')
        
        # change the internal state
        self.framePinHigh = True
    
    def cmd_slot_toggle(self):
        '''emulates
           void debugpins_slot_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_slot_toggle')
        
        # change the internal state
        self.slotPinHigh = not self.slotPinHigh
    
    def cmd_slot_clr(self):
        '''emulates
           void debugpins_slot_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_slot_clr')
        
        # change the internal state
        self.slotPinHigh = False
    
    def cmd_slot_set(self):
        '''emulates
           void debugpins_slot_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_slot_set')
        
        # change the internal state
        self.slotPinHigh = True
    
    def cmd_fsm_toggle(self):
        '''emulates
           void debugpins_fsm_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_fsm_toggle')
        
        # change the internal state
        self.fsmPinHigh = not self.fsmPinHigh
    
    def cmd_fsm_clr(self):
        '''emulates
           void debugpins_fsm_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_fsm_clr')
        
        # change the internal state
        self.fsmPinHigh = False
    
    def cmd_fsm_set(self):
        '''emulates
           void debugpins_fsm_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_fsm_set')
        
        # change the internal state
        self.fsmPinHigh = True
    
    def cmd_task_toggle(self):
        '''emulates
           void debugpins_task_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_task_toggle')
        
        # change the internal state
        self.taskPinHigh = not self.taskPinHigh
    
    def cmd_task_clr(self):
        '''emulates
           void debugpins_task_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_task_clr')
        
        # change the internal state
        self.taskPinHigh = False
    
    def cmd_task_set(self):
        '''emulates
           void debugpins_task_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_task_set')
        
        # change the internal state
        self.taskPinHigh = True
    
    def cmd_isr_toggle(self):
        '''emulates
           void debugpins_isr_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_isr_toggle')
        
        # change the internal state
        self.isrPinHigh = not self.isrPinHigh
    
    def cmd_isr_clr(self):
        '''emulates
           void debugpins_isr_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_isr_clr')
        
        # change the internal state
        self.isrPinHigh = False
    
    def cmd_isr_set(self):
        '''emulates
           void debugpins_isr_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_isr_set')
        
        # change the internal state
        self.isrPinHigh = True
    
    def cmd_radio_toggle(self):
        '''emulates
           void debugpins_radio_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioPinHigh = not self.radioPinHigh
    
    def cmd_radio_clr(self):
        '''emulates
           void debugpins_radio_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_clr')
        
        # change the internal state
        self.radioPinHigh = False
    
    def cmd_radio_set(self):
        '''emulates
           void debugpins_radio_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_set')
        
        # change the internal state
        self.radioPinHigh = True
    
    #=== getters
    
    def get_framePinHigh(self):
        return self.framePinHigh
    
    def get_slotPinHigh(self):
        return self.slotPinHigh
    
    def get_fsmPinHigh(self):
        return self.fsmPinHigh
    
    def get_isrPinHigh(self):
        return self.isrPinHigh
    
    def get_radioPinHigh(self):
        return self.radioPinHigh
    
    #======================== private =========================================