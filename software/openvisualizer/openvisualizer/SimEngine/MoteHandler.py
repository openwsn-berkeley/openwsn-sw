#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import threading
import socket
import logging
import os
import time
import binascii

from openvisualizer.SimEngine   import SimEngine
from openvisualizer.BspEmulator import BspBoard
from openvisualizer.BspEmulator import BspDebugpins
from openvisualizer.BspEmulator import BspEui64
from openvisualizer.BspEmulator import BspLeds
from openvisualizer.BspEmulator import BspRadio
from openvisualizer.BspEmulator import BspSctimer
from openvisualizer.BspEmulator import BspUart
from openvisualizer.BspEmulator import HwSupply
from openvisualizer.BspEmulator import HwCrystal

#============================ get notification IDs ============================
# Contains the list of notifIds used in the following functions.
notifString = []

def readNotifIds(headerPath):
    '''
    Contextual parent must call this method before other use of mote handler.
    
    ``headerPath`` Path to openwsnmodule_obj.h, containing notifIds
    
    Required since this module cannot know where to find the header file.
    '''
    import re

    f     = open(headerPath)
    lines = f.readlines()
    f.close()
    
    global notifString
    for line in lines:
        m = re.search('MOTE_NOTIF_(\w+)',line)
        if m:
            if m.group(1) not in notifString:
                notifString += [m.group(1)]

def notifId(s):
    assert s in notifString
    return notifString.index(s)

#============================ classes =========================================

class MoteHandler(threading.Thread):
    
    def __init__(self,mote):
        
        # store params
        self.engine          = SimEngine.SimEngine()
        self.mote            = mote
        
        #=== local variables
        self.loghandler      = self.engine.loghandler
        # unique identifier of the mote
        self.id              = self.engine.idmanager.getId()
        # position of the mote
        self.location        = self.engine.locationmanager.getLocation()
        # stats
        self.numRxCommands   = 0
        self.numTxCommands   = 0
        # hw
        self.hwSupply        = HwSupply.HwSupply(self)
        self.hwCrystal       = HwCrystal.HwCrystal(self)
        # bsp
        self.bspBoard        = BspBoard.BspBoard(self)
        self.bspDebugpins    = BspDebugpins.BspDebugpins(self)
        self.bspEui64        = BspEui64.BspEui64(self)
        self.bspLeds         = BspLeds.BspLeds(self)
        self.bspSctimer      = BspSctimer.BspSctimer(self)
        self.bspRadio        = BspRadio.BspRadio(self)
        self.bspUart         = BspUart.BspUart(self)
        # status
        self.booted          = False
        self.cpuRunning      = threading.Lock()
        self.cpuRunning.acquire()
        self.cpuDone         = threading.Lock()
        self.cpuDone.acquire()
        
        #=== install callbacks
        # board
        mote.set_callback(notifId('board_init'),                          self.bspBoard.cmd_init)
        mote.set_callback(notifId('board_sleep'),                         self.bspBoard.cmd_sleep)
        # debugpins
        mote.set_callback(notifId('debugpins_init'),                      self.bspDebugpins.cmd_init)
        mote.set_callback(notifId('debugpins_frame_toggle'),              self.bspDebugpins.cmd_frame_toggle)
        mote.set_callback(notifId('debugpins_frame_clr'),                 self.bspDebugpins.cmd_frame_clr)
        mote.set_callback(notifId('debugpins_frame_set'),                 self.bspDebugpins.cmd_frame_set)
        mote.set_callback(notifId('debugpins_slot_toggle'),               self.bspDebugpins.cmd_slot_toggle)
        mote.set_callback(notifId('debugpins_slot_clr'),                  self.bspDebugpins.cmd_slot_clr)
        mote.set_callback(notifId('debugpins_slot_set'),                  self.bspDebugpins.cmd_slot_set)
        mote.set_callback(notifId('debugpins_fsm_toggle'),                self.bspDebugpins.cmd_fsm_toggle)
        mote.set_callback(notifId('debugpins_fsm_clr'),                   self.bspDebugpins.cmd_fsm_clr)
        mote.set_callback(notifId('debugpins_fsm_set'),                   self.bspDebugpins.cmd_fsm_set)
        mote.set_callback(notifId('debugpins_task_toggle'),               self.bspDebugpins.cmd_task_toggle)
        mote.set_callback(notifId('debugpins_task_clr'),                  self.bspDebugpins.cmd_task_clr)
        mote.set_callback(notifId('debugpins_task_set'),                  self.bspDebugpins.cmd_task_set)
        mote.set_callback(notifId('debugpins_isr_toggle'),                self.bspDebugpins.cmd_isr_toggle)
        mote.set_callback(notifId('debugpins_isr_clr'),                   self.bspDebugpins.cmd_isr_clr)
        mote.set_callback(notifId('debugpins_isr_set'),                   self.bspDebugpins.cmd_isr_set)
        mote.set_callback(notifId('debugpins_radio_toggle'),              self.bspDebugpins.cmd_radio_toggle)
        mote.set_callback(notifId('debugpins_radio_clr'),                 self.bspDebugpins.cmd_radio_clr)
        mote.set_callback(notifId('debugpins_radio_set'),                 self.bspDebugpins.cmd_radio_set)
        mote.set_callback(notifId('debugpins_ka_clr'),                    self.bspDebugpins.cmd_ka_clr)
        mote.set_callback(notifId('debugpins_ka_set'),                    self.bspDebugpins.cmd_ka_set)
        mote.set_callback(notifId('debugpins_syncPacket_clr'),            self.bspDebugpins.cmd_syncPacket_clr)
        mote.set_callback(notifId('debugpins_syncPacket_set'),            self.bspDebugpins.cmd_syncPacket_set)
        mote.set_callback(notifId('debugpins_syncAck_clr'),               self.bspDebugpins.cmd_syncAck_clr)
        mote.set_callback(notifId('debugpins_syncAck_set'),               self.bspDebugpins.cmd_syncAck_set)
        mote.set_callback(notifId('debugpins_debug_clr'),                 self.bspDebugpins.cmd_debug_clr)
        mote.set_callback(notifId('debugpins_debug_set'),                 self.bspDebugpins.cmd_debug_set)
        # eui64
        mote.set_callback(notifId('eui64_get'),                           self.bspEui64.cmd_get)
        # leds
        mote.set_callback(notifId('leds_init'),                           self.bspLeds.cmd_init)
        mote.set_callback(notifId('leds_error_on'),                       self.bspLeds.cmd_error_on)
        mote.set_callback(notifId('leds_error_off'),                      self.bspLeds.cmd_error_off)
        mote.set_callback(notifId('leds_error_toggle'),                   self.bspLeds.cmd_error_toggle)
        mote.set_callback(notifId('leds_error_isOn'),                     self.bspLeds.cmd_error_isOn)
        mote.set_callback(notifId('leds_radio_on'),                       self.bspLeds.cmd_radio_on)
        mote.set_callback(notifId('leds_radio_off'),                      self.bspLeds.cmd_radio_off)
        mote.set_callback(notifId('leds_radio_toggle'),                   self.bspLeds.cmd_radio_toggle)
        mote.set_callback(notifId('leds_radio_isOn'),                     self.bspLeds.cmd_radio_isOn)
        mote.set_callback(notifId('leds_sync_on'),                        self.bspLeds.cmd_sync_on)
        mote.set_callback(notifId('leds_sync_off'),                       self.bspLeds.cmd_sync_off)
        mote.set_callback(notifId('leds_sync_toggle'),                    self.bspLeds.cmd_sync_toggle)
        mote.set_callback(notifId('leds_sync_isOn'),                      self.bspLeds.cmd_sync_isOn)
        mote.set_callback(notifId('leds_debug_on'),                       self.bspLeds.cmd_debug_on)
        mote.set_callback(notifId('leds_debug_off'),                      self.bspLeds.cmd_debug_off)
        mote.set_callback(notifId('leds_debug_toggle'),                   self.bspLeds.cmd_debug_toggle)
        mote.set_callback(notifId('leds_debug_isOn'),                     self.bspLeds.cmd_debug_isOn)
        mote.set_callback(notifId('leds_all_on'),                         self.bspLeds.cmd_all_on)
        mote.set_callback(notifId('leds_all_off'),                        self.bspLeds.cmd_all_off)
        mote.set_callback(notifId('leds_all_toggle'),                     self.bspLeds.cmd_all_toggle)
        mote.set_callback(notifId('leds_circular_shift'),                 self.bspLeds.cmd_circular_shift)
        mote.set_callback(notifId('leds_increment'),                      self.bspLeds.cmd_increment)
        # radio
        mote.set_callback(notifId('radio_init'),                          self.bspRadio.cmd_init)
        mote.set_callback(notifId('radio_reset'),                         self.bspRadio.cmd_reset)
        mote.set_callback(notifId('radio_setFrequency'),                  self.bspRadio.cmd_setFrequency)
        mote.set_callback(notifId('radio_rfOn'),                          self.bspRadio.cmd_rfOn)
        mote.set_callback(notifId('radio_rfOff'),                         self.bspRadio.cmd_rfOff)
        mote.set_callback(notifId('radio_loadPacket'),                    self.bspRadio.cmd_loadPacket)
        mote.set_callback(notifId('radio_txEnable'),                      self.bspRadio.cmd_txEnable)
        mote.set_callback(notifId('radio_txNow'),                         self.bspRadio.cmd_txNow)
        mote.set_callback(notifId('radio_rxEnable'),                      self.bspRadio.cmd_rxEnable)
        mote.set_callback(notifId('radio_rxNow'),                         self.bspRadio.cmd_rxNow)
        mote.set_callback(notifId('radio_getReceivedFrame'),              self.bspRadio.cmd_getReceivedFrame)
        # sctimer
        mote.set_callback(notifId('sctimer_init'),                        self.bspSctimer.cmd_init)
        mote.set_callback(notifId('sctimer_setCompare'),                  self.bspSctimer.cmd_setCompare)
        mote.set_callback(notifId('sctimer_readCounter'),                 self.bspSctimer.cmd_readCounter)
        mote.set_callback(notifId('sctimer_enable'),                      self.bspSctimer.cmd_enable)
        mote.set_callback(notifId('sctimer_disable'),                     self.bspSctimer.cmd_disable)
        # uart
        mote.set_callback(notifId('uart_init'),                           self.bspUart.cmd_init)
        mote.set_callback(notifId('uart_enableInterrupts'),               self.bspUart.cmd_enableInterrupts)
        mote.set_callback(notifId('uart_disableInterrupts'),              self.bspUart.cmd_disableInterrupts)
        mote.set_callback(notifId('uart_clearRxInterrupts'),              self.bspUart.cmd_clearRxInterrupts)
        mote.set_callback(notifId('uart_clearTxInterrupts'),              self.bspUart.cmd_clearTxInterrupts)
        mote.set_callback(notifId('uart_writeByte'),                      self.bspUart.cmd_writeByte)
        mote.set_callback(notifId('uart_writeCircularBuffer_FASTSIM'),    self.bspUart.cmd_writeCircularBuffer_FASTSIM)
        mote.set_callback(notifId('uart_writeBufferByLen_FASTSIM'),       self.bspUart.uart_writeBufferByLen_FASTSIM)
        mote.set_callback(notifId('uart_readByte'),                       self.bspUart.cmd_readByte)
        
        # logging this module
        self.log             = logging.getLogger('MoteHandler_'+str(self.id))
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.NullHandler())
        
        # logging this mote's modules
        for loggerName in [
                'MoteHandler_'+str(self.id),
                # hw
                'HwSupply_'+str(self.id),
                'HwCrystal_'+str(self.id),
                # bsp
                'BspBoard_'+str(self.id),
                'BspDebugpins_'+str(self.id),
                'BspEui64_'+str(self.id),
                'BspLeds_'+str(self.id),
                'BspSctimer_'+str(self.id),
                'BspRadio_'+str(self.id),
                'BspUart_'+str(self.id),
            ]:
            temp = logging.getLogger(loggerName)
            temp.setLevel(logging.INFO)
            temp.addHandler(self.loghandler)
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.setName('MoteHandler_'+str(self.id))
        
        # thread daemon mode
        self.setDaemon(True)
        
        # log
        self.log.info('thread initialized')
    
    def run(self):
    
        # log
        self.log.info('thread starting')
        
        # switch on the mote
        self.hwSupply.switchOn()
        
        assert 0
        
    #======================== public ==========================================
    
    def getId(self):
        return self.id
    
    def getLocation(self):
        return self.location
    
    def setLocation(self,lat,lon):
        self.location = (lat,lon)
    
    def handleEvent(self,functionToCall):
        
        if not self.booted:
            
            assert functionToCall==self.hwSupply.switchOn
            
            # I'm not booted
            self.booted = True
            
            # start the thread's execution
            self.start()
            
            # wait for CPU to be done
            self.cpuDone.acquire()
        
        else:
            # call the funcion (mote runs in ISR)
            kickScheduler = functionToCall()
            
            assert kickScheduler in [True,False]
            
            if kickScheduler:
                # release the mote's CPU (mote runs in task mode)
                self.cpuRunning.release()
                
                # wait for CPU to be done
                self.cpuDone.acquire()
    
    #======================== private =========================================
    