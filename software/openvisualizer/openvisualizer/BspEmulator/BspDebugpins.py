#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

from openvisualizer.SimEngine   import SimEngine
import BspModule
import VcdLogger

class BspDebugpins(BspModule.BspModule):
    '''
    Emulates the 'debugpins' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        self.motehandler          = motehandler
        
        # local variables
        self.timeline             = self.engine.timeline
        self.framePinHigh         = False
        self.slotPinHigh          = False
        self.fsmPinHigh           = False
        self.taskPinHigh          = False
        self.isrPinHigh           = False
        self.radioPinHigh         = False
        self.kaPinHigh            = False
        self.syncPacketPinHigh    = False
        self.syncAckPinHigh       = False
        self.debugPinHigh         = False
        self.vcdLogger            = VcdLogger.VcdLogger()
        
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
        
        # remember that module has been initialized
        self.isInitialized = True
    
    # frame
    
    def cmd_frame_toggle(self):
        '''emulates
           void debugpins_frame_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_frame_toggle')
        
        # change the internal state
        self.framePinHigh = not self.framePinHigh
        
        # log VCD
        self._logVcd('frame')
    
    def cmd_frame_clr(self):
        '''emulates
           void debugpins_frame_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_frame_clr')
        
        # change the internal state
        self.framePinHigh = False
        
        # log VCD
        self._logVcd('frame')
    
    def cmd_frame_set(self):
        '''emulates
           void debugpins_frame_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_frame_set')
        
        # change the internal state
        self.framePinHigh = True
        
        # log VCD
        self._logVcd('frame')
    
    # slot
    
    def cmd_slot_toggle(self):
        '''emulates
           void debugpins_slot_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_slot_toggle')
        
        # change the internal state
        self.slotPinHigh = not self.slotPinHigh
        
        # log VCD
        self._logVcd('slot')
    
    def cmd_slot_clr(self):
        '''emulates
           void debugpins_slot_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_slot_clr')
        
        # change the internal state
        self.slotPinHigh = False
        
        # log VCD
        self._logVcd('slot')
    
    def cmd_slot_set(self):
        '''emulates
           void debugpins_slot_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_slot_set')
        
        # change the internal state
        self.slotPinHigh = True
        
        # log VCD
        self._logVcd('slot')
    
    # fsm
    
    def cmd_fsm_toggle(self):
        '''emulates
           void debugpins_fsm_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_fsm_toggle')
        
        # change the internal state
        self.fsmPinHigh = not self.fsmPinHigh
        
        # log VCD
        self._logVcd('fsm')
    
    def cmd_fsm_clr(self):
        '''emulates
           void debugpins_fsm_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_fsm_clr')
        
        # change the internal state
        self.fsmPinHigh = False
        
        # log VCD
        self._logVcd('fsm')
    
    def cmd_fsm_set(self):
        '''emulates
           void debugpins_fsm_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_fsm_set')
        
        # change the internal state
        self.fsmPinHigh = True
        
        # log VCD
        self._logVcd('fsm')
    
    # task
    
    def cmd_task_toggle(self):
        '''emulates
           void debugpins_task_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_task_toggle')
        
        # change the internal state
        self.taskPinHigh = not self.taskPinHigh
        
        # log VCD
        self._logVcd('task')
    
    def cmd_task_clr(self):
        '''emulates
           void debugpins_task_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_task_clr')
        
        # change the internal state
        self.taskPinHigh = False
        
        # log VCD
        self._logVcd('task')
    
    def cmd_task_set(self):
        '''emulates
           void debugpins_task_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_task_set')
        
        # change the internal state
        self.taskPinHigh = True
        
        # log VCD
        self._logVcd('task')
    
    # isr
    
    def cmd_isr_toggle(self):
        '''emulates
           void debugpins_isr_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_isr_toggle')
        
        # change the internal state
        self.isrPinHigh = not self.isrPinHigh
        
        # log VCD
        self._logVcd('isr')
    
    def cmd_isr_clr(self):
        '''emulates
           void debugpins_isr_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_isr_clr')
        
        # change the internal state
        self.isrPinHigh = False
        
        # log VCD
        self._logVcd('isr')
    
    def cmd_isr_set(self):
        '''emulates
           void debugpins_isr_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_isr_set')
        
        # change the internal state
        self.isrPinHigh = True
        
        # log VCD
        self._logVcd('isr')
    
    # radio
    
    def cmd_radio_toggle(self):
        '''emulates
           void debugpins_radio_toggle()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_toggle')
        
        # change the internal state
        self.radioPinHigh = not self.radioPinHigh
        
        # log VCD
        self._logVcd('radio')
    
    def cmd_radio_clr(self):
        '''emulates
           void debugpins_radio_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_clr')
        
        # change the internal state
        self.radioPinHigh = False
        
        # log VCD
        self._logVcd('radio')
    
    def cmd_radio_set(self):
        '''emulates
           void debugpins_radio_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_radio_set')
        
        # change the internal state
        self.radioPinHigh = True
        
        # log VCD
        self._logVcd('radio')
    
    # ka
    
    def cmd_ka_clr(self):
        '''emulates
           void debugpins_ka_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_ka_clr')
        
        # change the internal state
        self.kaPinHigh = False
        
        # log VCD
        self._logVcd('ka')
    
    def cmd_ka_set(self):
        '''emulates
           void debugpins_ka_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_ka_set')
        
        # change the internal state
        self.kaPinHigh = True
        
        # log VCD
        self._logVcd('ka')
    
    # syncPacket
    
    def cmd_syncPacket_clr(self):
        '''emulates
           void debugpins_syncPacket_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_syncPacket_clr')
        
        # change the internal state
        self.syncPacketPinHigh = False
        
        # log VCD
        self._logVcd('syncPacket')
    
    def cmd_syncPacket_set(self):
        '''emulates
           void debugpins_syncPacket_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_syncPacket_set')
        
        # change the internal state
        self.syncPacketPinHigh = True
        
        # log VCD
        self._logVcd('syncPacket')
    
    # syncAck
    
    def cmd_syncAck_clr(self):
        '''emulates
           void debugpins_syncAck_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_syncAck_clr')
        
        # change the internal state
        self.syncAckPinHigh = False
        
        # log VCD
        self._logVcd('syncAck')
    
    def cmd_syncAck_set(self):
        '''emulates
           void debugpins_syncAck_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_syncAck_set')
        
        # change the internal state
        self.syncAckPinHigh = True
        
        # log VCD
        self._logVcd('syncAck')
    
    # debug
    
    def cmd_debug_clr(self):
        '''emulates
           void debugpins_debug_clr()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_debug_clr')
        
        # change the internal state
        self.debugPinHigh = False
        
        # log VCD
        self._logVcd('debug')
    
    def cmd_debug_set(self):
        '''emulates
           void debugpins_debug_set()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_debug_set')
        
        # change the internal state
        self.debugPinHigh = True
        
        # log VCD
        self._logVcd('debug')
    
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
    
    def get_kaPinHigh(self):
        return self.kaPinHigh
    
    def get_syncPacketPinHigh(self):
        return self.syncPacketPinHigh
    
    def get_syncAckPinHigh(self):
        return self.syncAckPinHigh
    
    def get_debugPinHigh(self):
        return self.debugPinHigh
    
    #======================== private =========================================
    
    def _logVcd(self,signal):
        self.vcdLogger.log(
            ts     = self.timeline.getCurrentTime(),
            mote   = self.motehandler.getId(),
            signal = signal,
            state  = getattr(self,'{0}PinHigh'.format(signal)),
        )