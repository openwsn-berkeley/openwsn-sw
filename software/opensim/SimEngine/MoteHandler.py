#!/usr/bin/python

import threading
import socket
import logging
import os
import time
import binascii

from BspEmulator import BspBoard
from BspEmulator import BspBsp_timer
from BspEmulator import BspDebugpins
from BspEmulator import BspEui64
from BspEmulator import BspLeds
from BspEmulator import BspRadio
from BspEmulator import BspRadiotimer
from BspEmulator import BspUart
from BspEmulator import HwSupply
from BspEmulator import HwCrystal

TCPRXBUFSIZE       = 4096    # size of the TCP reception buffer

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class MoteHandler(threading.Thread):
    '''
    \brief Handle the connection of a mote.
    '''
    
    commandIds = {
        #===== from client to server
        # board
        'OPENSIM_CMD_board_init'                      : 0,
        'OPENSIM_CMD_board_sleep'                     : 1,
        'OPENSIM_CMD_board_reset'                     : 2,
        # bsp_timer
        'OPENSIM_CMD_bsp_timer_init'                  : 3,
        'OPENSIM_CMD_bsp_timer_reset'                 : 4,
        'OPENSIM_CMD_bsp_timer_scheduleIn'            : 5,
        'OPENSIM_CMD_bsp_timer_cancel_schedule'       : 6,
        'OPENSIM_CMD_bsp_timer_get_currentValue'      : 7,
        # debugpins
        'OPENSIM_CMD_debugpins_init'                  : 8,
        'OPENSIM_CMD_debugpins_frame_toggle'          : 9,
        'OPENSIM_CMD_debugpins_frame_clr'             : 10,
        'OPENSIM_CMD_debugpins_frame_set'             : 11,
        'OPENSIM_CMD_debugpins_slot_toggle'           : 12,
        'OPENSIM_CMD_debugpins_slot_clr'              : 13,
        'OPENSIM_CMD_debugpins_slot_set'              : 14,
        'OPENSIM_CMD_debugpins_fsm_toggle'            : 15,
        'OPENSIM_CMD_debugpins_fsm_clr'               : 16,
        'OPENSIM_CMD_debugpins_fsm_set'               : 17,
        'OPENSIM_CMD_debugpins_task_toggle'           : 18,
        'OPENSIM_CMD_debugpins_task_clr'              : 19,
        'OPENSIM_CMD_debugpins_task_set'              : 20,
        'OPENSIM_CMD_debugpins_isr_toggle'            : 21,
        'OPENSIM_CMD_debugpins_isr_clr'               : 22,
        'OPENSIM_CMD_debugpins_isr_set'               : 23,
        'OPENSIM_CMD_debugpins_radio_toggle'          : 24,
        'OPENSIM_CMD_debugpins_radio_clr'             : 25,
        'OPENSIM_CMD_debugpins_radio_set'             : 26,
        # eui64
        'OPENSIM_CMD_eui64_get'                       : 27,
        # leds
        'OPENSIM_CMD_leds_init'                       : 28,
        'OPENSIM_CMD_leds_error_on'                   : 29,
        'OPENSIM_CMD_leds_error_off'                  : 30,
        'OPENSIM_CMD_leds_error_toggle'               : 31,
        'OPENSIM_CMD_leds_error_isOn'                 : 32,
        'OPENSIM_CMD_leds_error_blink'                : 33,
        'OPENSIM_CMD_leds_radio_on'                   : 34,
        'OPENSIM_CMD_leds_radio_off'                  : 35,
        'OPENSIM_CMD_leds_radio_toggle'               : 36,
        'OPENSIM_CMD_leds_radio_isOn'                 : 37,
        'OPENSIM_CMD_leds_sync_on'                    : 38,
        'OPENSIM_CMD_leds_sync_off'                   : 39,
        'OPENSIM_CMD_leds_sync_toggle'                : 40,
        'OPENSIM_CMD_leds_sync_isOn'                  : 41,
        'OPENSIM_CMD_leds_debug_on'                   : 42,
        'OPENSIM_CMD_leds_debug_off'                  : 43,
        'OPENSIM_CMD_leds_debug_toggle'               : 44,
        'OPENSIM_CMD_leds_debug_isOn'                 : 45,
        'OPENSIM_CMD_leds_all_on'                     : 46,
        'OPENSIM_CMD_leds_all_off'                    : 47,
        'OPENSIM_CMD_leds_all_toggle'                 : 48,
        'OPENSIM_CMD_leds_circular_shift'             : 49,
        'OPENSIM_CMD_leds_increment'                  : 50,
        # radio
        'OPENSIM_CMD_radio_init'                      : 51,
        'OPENSIM_CMD_radio_reset'                     : 52,
        'OPENSIM_CMD_radio_startTimer'                : 53,
        'OPENSIM_CMD_radio_getTimerValue'             : 54,
        'OPENSIM_CMD_radio_setTimerPeriod'            : 55,
        'OPENSIM_CMD_radio_getTimerPeriod'            : 56,
        'OPENSIM_CMD_radio_setFrequency'              : 57,
        'OPENSIM_CMD_radio_rfOn'                      : 58,
        'OPENSIM_CMD_radio_rfOff'                     : 59,
        'OPENSIM_CMD_radio_loadPacket'                : 60,
        'OPENSIM_CMD_radio_txEnable'                  : 61,
        'OPENSIM_CMD_radio_txNow'                     : 62,
        'OPENSIM_CMD_radio_rxEnable'                  : 63,
        'OPENSIM_CMD_radio_rxNow'                     : 64,
        'OPENSIM_CMD_radio_getReceivedFrame'          : 65,
        # radiotimer
        'OPENSIM_CMD_radiotimer_init'                 : 66,
        'OPENSIM_CMD_radiotimer_start'                : 67,
        'OPENSIM_CMD_radiotimer_getValue'             : 68,
        'OPENSIM_CMD_radiotimer_setPeriod'            : 69,
        'OPENSIM_CMD_radiotimer_getPeriod'            : 70,
        'OPENSIM_CMD_radiotimer_schedule'             : 71,
        'OPENSIM_CMD_radiotimer_cancel'               : 72,
        'OPENSIM_CMD_radiotimer_getCapturedTime'      : 73,
        # uart
        'OPENSIM_CMD_uart_init'                       : 74,
        'OPENSIM_CMD_uart_enableInterrupts'           : 75,
        'OPENSIM_CMD_uart_disableInterrupts'          : 76,
        'OPENSIM_CMD_uart_clearRxInterrupts'          : 77,
        'OPENSIM_CMD_uart_clearTxInterrupts'          : 78,
        'OPENSIM_CMD_uart_writeByte'                  : 79,
        'OPENSIM_CMD_uart_readByte'                   : 80,
        # supply
        #===== from server to client
        # board
        # bsp_timer
        'OPENSIM_CMD_bsp_timer_isr'                   : 100,
        # debugpins
        # eui64
        # leds
        # radio
        'OPENSIM_CMD_radio_isr_startFrame'            : 101,
        'OPENSIM_CMD_radio_isr_endFrame'              : 102,
        # radiotimer
        'OPENSIM_CMD_radiotimer_isr_compare'          : 103,
        'OPENSIM_CMD_radiotimer_isr_overflow'         : 104,
        # uart
        'OPENSIM_CMD_uart_isr_tx'                     : 105,
        'OPENSIM_CMD_uart_isr_rx'                     : 106,
        # supply
        'OPENSIM_CMD_supply_on'                       : 107,
        'OPENSIM_CMD_supply_off'                      : 108,
    }
    
    def __init__(self,engine,mote):
        
        # store params
        self.engine          = engine
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
        self.hwSupply        = HwSupply.HwSupply(self.engine,self)
        self.hwCrystal       = HwCrystal.HwCrystal(self.engine,self)
        # bsp
        self.bspBoard        = BspBoard.BspBoard(self.engine,self)
        self.bspBsp_timer    = BspBsp_timer.BspBsp_timer(self.engine,self)
        self.bspDebugpins    = BspDebugpins.BspDebugpins(self.engine,self)
        self.bspEui64        = BspEui64.BspEui64(self.engine,self)
        self.bspLeds         = BspLeds.BspLeds(self.engine,self)
        self.bspRadiotimer   = BspRadiotimer.BspRadiotimer(self.engine,self)
        self.bspRadio        = BspRadio.BspRadio(self.engine,self)
        self.bspUart         = BspUart.BspUart(self.engine,self)
        
        #=== install callbacks
        # board
        mote.set_callback(notifId('board_init'),                self.bspBoard.cmd_init)
        mote.set_callback(notifId('board_sleep'),               self.bspBoard.cmd_sleep)
        # bsp_timer
        mote.set_callback(notifId('timer_init'),                self.bspBsp_timer.cmd_init)
        mote.set_callback(notifId('bsp_timer_reset'),           self.bspBsp_timer.cmd_reset)
        mote.set_callback(notifId('bsp_timer_scheduleIn'),      self.bspBsp_timer.cmd_scheduleIn)
        mote.set_callback(notifId('bsp_timer_cancel_schedule'), self.bspBsp_timer.cmd_cancel_schedule)
        mote.set_callback(notifId('bsp_timer_get_currentValue'),self.bspBsp_timer.cmd_get_currentValue)
        # debugpins
        mote.set_callback(notifId('debugpins_init'),            self.bspDebugpins.cmd_init)
        mote.set_callback(notifId('debugpins_frame_toggle'),    self.bspDebugpins.cmd_frame_toggle)
        mote.set_callback(notifId('debugpins_frame_clr'),       self.bspDebugpins.cmd_frame_clr)
        mote.set_callback(notifId('debugpins_frame_set'),       self.bspDebugpins.cmd_frame_set)
        mote.set_callback(notifId('debugpins_slot_toggle'),     self.bspDebugpins.cmd_slot_toggle)
        mote.set_callback(notifId('debugpins_slot_clr'),        self.bspDebugpins.cmd_slot_clr)
        mote.set_callback(notifId('debugpins_slot_set'),        self.bspDebugpins.cmd_slot_set)
        mote.set_callback(notifId('debugpins_fsm_toggle'),      self.bspDebugpins.cmd_fsm_toggle)
        mote.set_callback(notifId('debugpins_fsm_clr'),         self.bspDebugpins.cmd_fsm_clr)
        mote.set_callback(notifId('debugpins_fsm_set'),         self.bspDebugpins.cmd_fsm_set)
        mote.set_callback(notifId('debugpins_task_toggle'),     self.bspDebugpins.cmd_task_toggle)
        mote.set_callback(notifId('debugpins_task_clr'),        self.bspDebugpins.cmd_task_clr)
        mote.set_callback(notifId('debugpins_task_set'),        self.bspDebugpins.cmd_task_set)
        mote.set_callback(notifId('debugpins_isr_toggle'),      self.bspDebugpins.cmd_isr_toggle)
        mote.set_callback(notifId('debugpins_isr_clr'),         self.bspDebugpins.cmd_isr_clr)
        mote.set_callback(notifId('debugpins_isr_set'),         self.bspDebugpins.cmd_isr_set)
        mote.set_callback(notifId('debugpins_radio_toggle'),    self.bspDebugpins.cmd_radio_toggle)
        mote.set_callback(notifId('debugpins_radio_clr'),       self.bspDebugpins.cmd_radio_clr)
        mote.set_callback(notifId('debugpins_radio_set'),       self.bspDebugpins.cmd_radio_set)
        # eui64
        mote.set_callback(notifId('eui64_get'),                 self.bspEui64.cmd_get)
        # leds
        mote.set_callback(notifId('leds_init'),                 self.bspLeds.cmd_init)
        mote.set_callback(notifId('leds_error_on'),             self.bspLeds.cmd_error_on)
        mote.set_callback(notifId('leds_error_off'),            self.bspLeds.cmd_error_off)
        mote.set_callback(notifId('leds_error_toggle'),         self.bspLeds.cmd_error_toggle)
        mote.set_callback(notifId('leds_error_isOn'),           self.bspLeds.cmd_error_isOn)
        mote.set_callback(notifId('leds_radio_on'),             self.bspLeds.cmd_radio_on)
        mote.set_callback(notifId('leds_radio_off'),            self.bspLeds.cmd_radio_off)
        mote.set_callback(notifId('leds_radio_toggle'),         self.bspLeds.cmd_radio_toggle)
        mote.set_callback(notifId('leds_radio_isOn'),           self.bspLeds.cmd_radio_isOn)
        mote.set_callback(notifId('leds_sync_on'),              self.bspLeds.cmd_sync_on)
        mote.set_callback(notifId('leds_sync_off'),             self.bspLeds.cmd_sync_off)
        mote.set_callback(notifId('leds_sync_toggle'),          self.bspLeds.cmd_sync_toggle)
        mote.set_callback(notifId('leds_sync_isOn'),            self.bspLeds.cmd_sync_isOn)
        mote.set_callback(notifId('leds_debug_on'),             self.bspLeds.cmd_debug_on)
        mote.set_callback(notifId('leds_debug_off'),            self.bspLeds.cmd_debug_off)
        mote.set_callback(notifId('leds_debug_toggle'),         self.bspLeds.cmd_debug_toggle)
        mote.set_callback(notifId('leds_debug_isOn'),           self.bspLeds.cmd_debug_isOn)
        mote.set_callback(notifId('leds_all_on'),               self.bspLeds.cmd_all_on)
        mote.set_callback(notifId('leds_all_off'),              self.bspLeds.cmd_all_off)
        mote.set_callback(notifId('leds_all_toggle'),           self.bspLeds.cmd_all_toggle)
        mote.set_callback(notifId('leds_circular_shift'),       self.bspLeds.cmd_circular_shift)
        mote.set_callback(notifId('leds_increment'),            self.bspLeds.cmd_increment)
        # radio
        mote.set_callback(notifId('radio_init'),                self.bspRadio.cmd_init)
        mote.set_callback(notifId('radio_reset'),               self.bspRadio.cmd_reset)
        mote.set_callback(notifId('radio_startTimer'),          self.bspRadio.cmd_startTimer)
        mote.set_callback(notifId('radio_getTimerValue'),       self.bspRadio.cmd_getTimerValue)
        mote.set_callback(notifId('radio_setTimerPeriod'),      self.bspRadio.cmd_setTimerPeriod)
        mote.set_callback(notifId('radio_getTimerPeriod'),      self.bspRadio.cmd_getTimerPeriod)
        mote.set_callback(notifId('radio_setFrequency'),        self.bspRadio.cmd_setFrequency)
        mote.set_callback(notifId('radio_rfOn'),                self.bspRadio.cmd_rfOn)
        mote.set_callback(notifId('radio_rfOff'),               self.bspRadio.cmd_rfOff)
        mote.set_callback(notifId('radio_loadPacket'),          self.bspRadio.cmd_loadPacket)
        mote.set_callback(notifId('radio_txEnable'),            self.bspRadio.cmd_txEnable)
        mote.set_callback(notifId('radio_txNow'),               self.bspRadio.cmd_txNow)
        mote.set_callback(notifId('radio_rxEnable'),            self.bspRadio.cmd_rxEnable)
        mote.set_callback(notifId('radio_rxNow'),               self.bspRadio.cmd_rxNow)
        mote.set_callback(notifId('radio_getReceivedFrame'),    self.bspRadio.cmd_getReceivedFrame)
        # radiotimer
        mote.set_callback(notifId('radiotimer_init'),           self.bspRadiotimer.cmd_init)
        mote.set_callback(notifId('radiotimer_start'),          self.bspRadiotimer.cmd_start)
        mote.set_callback(notifId('radiotimer_getValue'),       self.bspRadiotimer.cmd_getValue)
        mote.set_callback(notifId('radiotimer_setPeriod'),      self.bspRadiotimer.cmd_setPeriod)
        mote.set_callback(notifId('radiotimer_getPeriod'),      self.bspRadiotimer.cmd_getPeriod)
        mote.set_callback(notifId('radiotimer_schedule'),       self.bspRadiotimer.cmd_schedule)
        mote.set_callback(notifId('radiotimer_cancel'),         self.bspRadiotimer.cmd_cancel)
        mote.set_callback(notifId('radiotimer_getCapturedTime'),self.bspRadiotimer.cmd_getCapturedTime)
        # uart
        mote.set_callback(notifId('uart_init'),                 self.bspUart.cmd_init)
        mote.set_callback(notifId('uart_enableInterrupts'),     self.bspUart.cmd_enableInterrupts)
        mote.set_callback(notifId('uart_disableInterrupts'),    self.bspUart.cmd_disableInterrupts)
        mote.set_callback(notifId('uart_clearRxInterrupts'),    self.bspUart.cmd_clearRxInterrupts)
        mote.set_callback(notifId('uart_clearTxInterrupts'),    self.bspUart.cmd_clearTxInterrupts)
        mote.set_callback(notifId('uart_writeByte'),            self.bspUart.cmd_writeByte)
        mote.set_callback(notifId('uart_readByte'),             self.bspUart.cmd_readByte)
        
        # logging this module
        self.log             = logging.getLogger('MoteHandler_'+str(self.id))
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # logging this mote's modules
        for loggerName in [
                'MoteHandler_'+str(self.id),
                # hw
                'HwSupply_'+str(self.id),
                'HwCrystal_'+str(self.id),
                # bsp
                'BspBoard_'+str(self.id),
                'BspBsp_timer_'+str(self.id),
                'BspDebugpins_'+str(self.id),
                'BspEui64_'+str(self.id),
                'BspLeds_'+str(self.id),
                'BspRadiotimer_'+str(self.id),
                'BspRadio_'+str(self.id),
                'BspUart_'+str(self.id),
            ]:
            temp = logging.getLogger(loggerName)
            temp.setLevel(logging.DEBUG)
            temp.addHandler(self.loghandler)
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.setName('MoteHandler_'+str(self.id))
        
        # thread daemon mode
        self.setDaemon(True)
    
    def run(self):
    
        # log
        self.log.info('starting')
        
        while(1):
            # wait for a command
            try:
                input = self.conn.recv(TCPRXBUFSIZE)
            except socket.error as err:
                self.log.critical('connection error (err='+str(err)+')')
                break
            
            # make sure I received something
            assert(len(input)>0)
            
            # handle the received packet
            self._handleReceivedCommand(input)
            
    #======================== public ==========================================
    
    def getId(self):
        return self.id
    
    def getLocation(self):
        return self.location
    
    def sendCommand(self,commandId,params=[]):
        
        # log
        self.log.debug('sending command='+self._cmdIdToName(commandId))
        
        # update statistics
        self.numTxCommands += 1
        
        # send command over connection
        dataToSend  = ''
        dataToSend += chr(commandId)
        for c in params:
            dataToSend += chr(c)
        self.conn.sendall(dataToSend)
    
    #======================== private =========================================
    
    def _handleReceivedCommand(self,input):
        
        # get the command id and params from the received command
        cmdId  = ord(input[0])
        params = input[1:]
        
        # log
        self.log.debug('received command='+self._cmdIdToName(cmdId))
        
        # update statistics
        self.numRxCommands += 1
        
        # make sure I know what callback to call
        assert(cmdId in self.commandCallbacks)
        
        # call the callback
        try:
            returnVal = self.commandCallbacks[cmdId](params)
        except Exception as err:
            self.log.critical(str(err))
            self.engine.pause()
            raise
    
    def _cmdIdToName(self,cmdId):
        cmdName = 'unknow'
        for k,v in self.commandIds.items():
            if cmdId==v:
                cmdName = k
                break
        return cmdName