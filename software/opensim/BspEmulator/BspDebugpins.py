#!/usr/bin/python

import BspModule

class BspDebugpins(BspModule.BspModule):
    '''
    \brief Emulates the 'debugpins' BSP module
    '''
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.frameHigh  = False
        self.slotHigh   = False
        self.fsmHigh    = False
        self.taskHigh   = False
        self.isrHigh    = False
        self.radioHigh  = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspDebugpins')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_frame_toggle(self):
        
        # log the activity
        self.log.debug('cmd_frame_toggle')
        
        # change the internal state
        self.frameHigh = not self.frameHigh
    
    def cmd_frame_clr(self):
        
        # log the activity
        self.log.debug('cmd_frame_clr')
        
        # change the internal state
        self.frameHigh = False      
    
    def cmd_frame_set(self):
        
        # log the activity
        self.log.debug('cmd_frame_set')
        
        # change the internal state
        self.frameHigh = True
    
    def cmd_slot_toggle(self):
        
        # log the activity
        self.log.debug('cmd_slot_toggle')
        
        # change the internal state
        self.slotHigh = not self.slotHigh
    
    def cmd_slot_clr(self):
        
        # log the activity
        self.log.debug('cmd_slot_clr')
        
        # change the internal state
        self.slotHigh = False
    
    def cmd_slot_set(self):
        
        # log the activity
        self.log.debug('cmd_slot_set')
        
        # change the internal state
        self.slotHigh = True
    
    def cmd_fsm_toggle(self):
        
        # log the activity
        self.log.debug('cmd_fsm_toggle')
        
        # change the internal state
        self.fsmHigh = not self.fsmHigh
    
    def cmd_fsm_clr(self):
        
        # log the activity
        self.log.debug('cmd_fsm_clr')
        
        # change the internal state
        self.fsmHigh = False
    
    def cmd_fsm_set(self):
        
        # log the activity
        self.log.debug('cmd_fsm_set')
        
        # change the internal state
        self.fsmHigh = True
    
    def cmd_task_toggle(self):
        
        # log the activity
        self.log.debug('cmd_task_toggle')
        
        # change the internal state
        self.taskHigh = not self.taskHigh
    
    def cmd_task_clr(self):
        
        # log the activity
        self.log.debug('cmd_task_clr')
        
        # change the internal state
        self.taskHigh = False
    
    def cmd_task_set(self):
        
        # log the activity
        self.log.debug('cmd_task_set')
        
        # change the internal state
        self.taskHigh = True
    
    def cmd_isr_toggle(self):
        
        # log the activity
        self.log.debug('cmd_isr_toggle')
        
        # change the internal state
        self.isrHigh = not self.isrHigh
    
    def cmd_isr_clr(self):
        
        # log the activity
        self.log.debug('cmd_isr_clr')
        
        # change the internal state
        self.isrHigh = False
    
    def cmd_isr_set(self):
        
        # log the activity
        self.log.debug('cmd_isr_set')
        
        # change the internal state
        self.isrHigh = True
    
    def cmd_radio_toggle(self):
        
        # log the activity
        self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioHigh = not self.radioHigh
    
    def cmd_radio_clr(self):
        
        # log the activity
        self.log.debug('cmd_radio_clr')
        
        # change the internal state
        self.radioHigh = False
    
    def cmd_radio_set(self):
        
        # log the activity
        self.log.debug('cmd_radio_set')
        
        # change the internal state
        self.radioHigh = True
    
    #=== getters
    
    def get_frameHigh(self):
        return frameHigh
    
    def get_slotHigh(self):
        return slotHigh
    
    def get_fsmHigh(self):
        return fsmHigh
    
    def get_isrHigh(self):
        return isrHigh
    
    def get_radioHigh(self):
        return radioHigh
    
    #======================== private =========================================