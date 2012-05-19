#!/usr/bin/python

import BspModule

class BspDebugpins(BspModule.BspModule):
    '''
    \brief Emulates the 'debugpins' BSP module
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
    
    def cmd_init(self,params):
        '''emulates
           void debugpins_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_init'])
    
    def cmd_frame_toggle(self,params):
        '''emulates
           void debugpins_frame_toggle()'''
        
        # log the activity
        self.log.debug('cmd_frame_toggle')
        
        # change the internal state
        self.framePinHigh = not self.framePinHigh
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_frame_toggle'])
    
    def cmd_frame_clr(self,params):
        '''emulates
           void debugpins_frame_clr()'''
        
        # log the activity
        self.log.debug('cmd_frame_clr')
        
        # change the internal state
        self.framePinHigh = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_frame_clr'])
    
    def cmd_frame_set(self,params):
        '''emulates
           void debugpins_frame_set()'''
        
        # log the activity
        self.log.debug('cmd_frame_set')
        
        # change the internal state
        self.framePinHigh = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_frame_set'])
    
    def cmd_slot_toggle(self,params):
        '''emulates
           void debugpins_slot_toggle()'''
        
        # log the activity
        self.log.debug('cmd_slot_toggle')
        
        # change the internal state
        self.slotPinHigh = not self.slotPinHigh
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_slot_toggle'])
    
    def cmd_slot_clr(self,params):
        '''emulates
           void debugpins_slot_clr()'''
        
        # log the activity
        self.log.debug('cmd_slot_clr')
        
        # change the internal state
        self.slotPinHigh = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_slot_clr'])
    
    def cmd_slot_set(self,params):
        '''emulates
           void debugpins_slot_set()'''
        
        # log the activity
        self.log.debug('cmd_slot_set')
        
        # change the internal state
        self.slotPinHigh = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_slot_set'])
    
    def cmd_fsm_toggle(self,params):
        '''emulates
           void debugpins_fsm_toggle()'''
        
        # log the activity
        self.log.debug('cmd_fsm_toggle')
        
        # change the internal state
        self.fsmPinHigh = not self.fsmPinHigh
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_fsm_toggle'])
    
    def cmd_fsm_clr(self,params):
        '''emulates
           void debugpins_fsm_clr()'''
        
        # log the activity
        self.log.debug('cmd_fsm_clr')
        
        # change the internal state
        self.fsmPinHigh = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_fsm_clr'])
    
    def cmd_fsm_set(self,params):
        '''emulates
           void debugpins_fsm_set()'''
        
        # log the activity
        self.log.debug('cmd_fsm_set')
        
        # change the internal state
        self.fsmPinHigh = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_fsm_set'])
    
    def cmd_task_toggle(self,params):
        '''emulates
           void debugpins_task_toggle()'''
        
        # log the activity
        self.log.debug('cmd_task_toggle')
        
        # change the internal state
        self.taskPinHigh = not self.taskPinHigh
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_task_toggle'])
    
    def cmd_task_clr(self,params):
        '''emulates
           void debugpins_task_clr()'''
        
        # log the activity
        self.log.debug('cmd_task_clr')
        
        # change the internal state
        self.taskPinHigh = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_task_clr'])
    
    def cmd_task_set(self,params):
        '''emulates
           void debugpins_task_set()'''
        
        # log the activity
        self.log.debug('cmd_task_set')
        
        # change the internal state
        self.taskPinHigh = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_task_set'])
    
    def cmd_isr_toggle(self,params):
        '''emulates
           void debugpins_isr_toggle()'''
        
        # log the activity
        self.log.debug('cmd_isr_toggle')
        
        # change the internal state
        self.isrPinHigh = not self.isrPinHigh
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_isr_toggle'])
    
    def cmd_isr_clr(self,params):
        '''emulates
           void debugpins_isr_clr()'''
        
        # log the activity
        self.log.debug('cmd_isr_clr')
        
        # change the internal state
        self.isrPinHigh = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_isr_clr'])
    
    def cmd_isr_set(self,params):
        '''emulates
           void debugpins_isr_set()'''
        
        # log the activity
        self.log.debug('cmd_isr_set')
        
        # change the internal state
        self.isrPinHigh = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_isr_set'])
    
    def cmd_radio_toggle(self,params):
        '''emulates
           void debugpins_radio_toggle()'''
        
        # log the activity
        self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioPinHigh = not self.radioPinHigh
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_radio_toggle'])
    
    def cmd_radio_clr(self,params):
        '''emulates
           void debugpins_radio_clr()'''
        
        # log the activity
        self.log.debug('cmd_radio_clr')
        
        # change the internal state
        self.radioPinHigh = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_radio_clr'])
    
    def cmd_radio_set(self,params):
        '''emulates
           void debugpins_radio_set()'''
        
        # log the activity
        self.log.debug('cmd_radio_set')
        
        # change the internal state
        self.radioPinHigh = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_debugpins_radio_set'])
    
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