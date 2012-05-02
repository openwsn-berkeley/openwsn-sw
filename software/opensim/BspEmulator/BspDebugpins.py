#!/usr/bin/python

import BspModule

class BspDebugpins(BspModule.BspModule):
    '''
    \brief Emulates the 'debugpins' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
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
    
    def cmd_frame_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_frame_toggle')
        
        # change the internal state
        self.framePinHigh = not self.framePinHigh
    
    def cmd_frame_clr(self,params):
        
        # log the activity
        self.log.debug('cmd_frame_clr')
        
        # change the internal state
        self.framePinHigh = False      
    
    def cmd_frame_set(self,params):
        
        # log the activity
        self.log.debug('cmd_frame_set')
        
        # change the internal state
        self.framePinHigh = True
    
    def cmd_slot_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_slot_toggle')
        
        # change the internal state
        self.slotPinHigh = not self.slotPinHigh
    
    def cmd_slot_clr(self,params):
        
        # log the activity
        self.log.debug('cmd_slot_clr')
        
        # change the internal state
        self.slotPinHigh = False
    
    def cmd_slot_set(self,params):
        
        # log the activity
        self.log.debug('cmd_slot_set')
        
        # change the internal state
        self.slotPinHigh = True
    
    def cmd_fsm_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_fsm_toggle')
        
        # change the internal state
        self.fsmPinHigh = not self.fsmPinHigh
    
    def cmd_fsm_clr(self,params):
        
        # log the activity
        self.log.debug('cmd_fsm_clr')
        
        # change the internal state
        self.fsmPinHigh = False
    
    def cmd_fsm_set(self,params):
        
        # log the activity
        self.log.debug('cmd_fsm_set')
        
        # change the internal state
        self.fsmPinHigh = True
    
    def cmd_task_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_task_toggle')
        
        # change the internal state
        self.taskPinHigh = not self.taskPinHigh
    
    def cmd_task_clr(self,params):
        
        # log the activity
        self.log.debug('cmd_task_clr')
        
        # change the internal state
        self.taskPinHigh = False
    
    def cmd_task_set(self,params):
        
        # log the activity
        self.log.debug('cmd_task_set')
        
        # change the internal state
        self.taskPinHigh = True
    
    def cmd_isr_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_isr_toggle')
        
        # change the internal state
        self.isrPinHigh = not self.isrPinHigh
    
    def cmd_isr_clr(self,params):
        
        # log the activity
        self.log.debug('cmd_isr_clr')
        
        # change the internal state
        self.isrPinHigh = False
    
    def cmd_isr_set(self,params):
        
        # log the activity
        self.log.debug('cmd_isr_set')
        
        # change the internal state
        self.isrPinHigh = True
    
    def cmd_radio_toggle(self,params):
        
        # log the activity
        self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioPinHigh = not self.radioPinHigh
    
    def cmd_radio_clr(self,params):
        
        # log the activity
        self.log.debug('cmd_radio_clr')
        
        # change the internal state
        self.radioPinHigh = False
    
    def cmd_radio_set(self,params):
        
        # log the activity
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