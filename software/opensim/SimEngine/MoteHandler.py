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
        # bsp_timer
        'OPENSIM_CMD_bsp_timer_init'                  : 2,
        'OPENSIM_CMD_bsp_timer_reset'                 : 3,
        'OPENSIM_CMD_bsp_timer_scheduleIn'            : 4,
        'OPENSIM_CMD_bsp_timer_cancel_schedule'       : 5,
        'OPENSIM_CMD_bsp_timer_get_currentValue'      : 6,
        # debugpins
        'OPENSIM_CMD_debugpins_init'                  : 7,
        'OPENSIM_CMD_debugpins_frame_toggle'          : 8,
        'OPENSIM_CMD_debugpins_frame_clr'             : 9,
        'OPENSIM_CMD_debugpins_frame_set'             : 10,
        'OPENSIM_CMD_debugpins_slot_toggle'           : 11,
        'OPENSIM_CMD_debugpins_slot_clr'              : 12,
        'OPENSIM_CMD_debugpins_slot_set'              : 13,
        'OPENSIM_CMD_debugpins_fsm_toggle'            : 14,
        'OPENSIM_CMD_debugpins_fsm_clr'               : 15,
        'OPENSIM_CMD_debugpins_fsm_set'               : 16,
        'OPENSIM_CMD_debugpins_task_toggle'           : 17,
        'OPENSIM_CMD_debugpins_task_clr'              : 18,
        'OPENSIM_CMD_debugpins_task_set'              : 19,
        'OPENSIM_CMD_debugpins_isr_toggle'            : 20,
        'OPENSIM_CMD_debugpins_isr_clr'               : 21,
        'OPENSIM_CMD_debugpins_isr_set'               : 22,
        'OPENSIM_CMD_debugpins_radio_toggle'          : 23,
        'OPENSIM_CMD_debugpins_radio_clr'             : 24,
        'OPENSIM_CMD_debugpins_radio_set'             : 25,
        # eui64
        'OPENSIM_CMD_eui64_get'                       : 26,
        # leds
        'OPENSIM_CMD_leds_init'                       : 27,
        'OPENSIM_CMD_leds_error_on'                   : 28,
        'OPENSIM_CMD_leds_error_off'                  : 29,
        'OPENSIM_CMD_leds_error_toggle'               : 30,
        'OPENSIM_CMD_leds_error_isOn'                 : 31,
        'OPENSIM_CMD_leds_radio_on'                   : 32,
        'OPENSIM_CMD_leds_radio_off'                  : 33,
        'OPENSIM_CMD_leds_radio_toggle'               : 34,
        'OPENSIM_CMD_leds_radio_isOn'                 : 35,
        'OPENSIM_CMD_leds_sync_on'                    : 36,
        'OPENSIM_CMD_leds_sync_off'                   : 37,
        'OPENSIM_CMD_leds_sync_toggle'                : 38,
        'OPENSIM_CMD_leds_sync_isOn'                  : 39,
        'OPENSIM_CMD_leds_debug_on'                   : 40,
        'OPENSIM_CMD_leds_debug_off'                  : 41,
        'OPENSIM_CMD_leds_debug_toggle'               : 42,
        'OPENSIM_CMD_leds_debug_isOn'                 : 43,
        'OPENSIM_CMD_leds_all_on'                     : 44,
        'OPENSIM_CMD_leds_all_off'                    : 45,
        'OPENSIM_CMD_leds_all_toggle'                 : 46,
        'OPENSIM_CMD_leds_circular_shift'             : 47,
        'OPENSIM_CMD_leds_increment'                  : 48,
        # radio
        'OPENSIM_CMD_radio_init'                      : 49,
        'OPENSIM_CMD_radio_reset'                     : 50,
        'OPENSIM_CMD_radio_startTimer'                : 51,
        'OPENSIM_CMD_radio_getTimerValue'             : 52,
        'OPENSIM_CMD_radio_setTimerPeriod'            : 53,
        'OPENSIM_CMD_radio_getTimerPeriod'            : 54,
        'OPENSIM_CMD_radio_setFrequency'              : 55,
        'OPENSIM_CMD_radio_rfOn'                      : 56,
        'OPENSIM_CMD_radio_rfOff'                     : 57,
        'OPENSIM_CMD_radio_loadPacket'                : 58,
        'OPENSIM_CMD_radio_txEnable'                  : 59,
        'OPENSIM_CMD_radio_txNow'                     : 60,
        'OPENSIM_CMD_radio_rxEnable'                  : 61,
        'OPENSIM_CMD_radio_rxNow'                     : 62,
        'OPENSIM_CMD_radio_getReceivedFrame'          : 63,
        # radiotimer
        'OPENSIM_CMD_radiotimer_init'                 : 64,
        'OPENSIM_CMD_radiotimer_start'                : 65,
        'OPENSIM_CMD_radiotimer_getValue'             : 66,
        'OPENSIM_CMD_radiotimer_setPeriod'            : 67,
        'OPENSIM_CMD_radiotimer_getPeriod'            : 68,
        'OPENSIM_CMD_radiotimer_schedule'             : 69,
        'OPENSIM_CMD_radiotimer_cancel'               : 70,
        'OPENSIM_CMD_radiotimer_getCapturedTime'      : 71,
        # uart
        'OPENSIM_CMD_uart_init'                       : 72,
        'OPENSIM_CMD_uart_enableInterrupts'           : 73,
        'OPENSIM_CMD_uart_disableInterrupts'          : 74,
        'OPENSIM_CMD_uart_clearRxInterrupts'          : 75,
        'OPENSIM_CMD_uart_clearTxInterrupts'          : 76,
        'OPENSIM_CMD_uart_writeByte'                  : 77,
        'OPENSIM_CMD_uart_readByte'                   : 78,
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
    
    def __init__(self,engine,conn,addr,port):
        
        # store params
        self.engine               = engine
        self.conn                 = conn
        self.addr                 = addr
        self.port                 = port
        
        #=== local variables
        # stats
        self.numRxCommands        = 0
        self.numTxCommands        = 0
        # hw
        self.hwSupply             = HwSupply.HwSupply(self)
        self.hwCrystal            = HwCrystal.HwCrystal(
                                            self,
                                            self.engine.timeline,
                                            32768)
        # bsp
        self.bspBoard             = BspBoard.BspBoard(
                                            self,
                                            self.engine.timeline)
        self.bspBsp_timer         = BspBsp_timer.BspBsp_timer(self)
        self.bspDebugpins         = BspDebugpins.BspDebugpins(self)
        self.bspEui64             = BspEui64.BspEui64(self)
        self.bspLeds              = BspLeds.BspLeds(self)
        self.bspRadio             = BspRadio.BspRadio(self)
        self.bspRadiotimer        = BspRadiotimer.BspRadiotimer(
                                            self,
                                            self.engine.timeline,
                                            self.hwCrystal)
        self.bspUart              = BspUart.BspUart(self)
        
        self.commandCallbacks = {
            # board
            self.commandIds['OPENSIM_CMD_board_init']                : self.bspBoard.cmd_init,
            self.commandIds['OPENSIM_CMD_board_sleep']               : self.bspBoard.cmd_sleep,
            # bsp_timer
            self.commandIds['OPENSIM_CMD_bsp_timer_init']            : self.bspBsp_timer.cmd_init,
            self.commandIds['OPENSIM_CMD_bsp_timer_reset']           : self.bspBsp_timer.cmd_reset,
            self.commandIds['OPENSIM_CMD_bsp_timer_scheduleIn']      : self.bspBsp_timer.cmd_scheduleIn,
            self.commandIds['OPENSIM_CMD_bsp_timer_cancel_schedule'] : self.bspBsp_timer.cmd_cancel_schedule,
            # debugpins
            self.commandIds['OPENSIM_CMD_debugpins_init']            : self.bspDebugpins.cmd_init,
            self.commandIds['OPENSIM_CMD_debugpins_frame_toggle']    : self.bspDebugpins.cmd_frame_toggle,
            self.commandIds['OPENSIM_CMD_debugpins_frame_clr']       : self.bspDebugpins.cmd_frame_clr,
            self.commandIds['OPENSIM_CMD_debugpins_frame_set']       : self.bspDebugpins.cmd_frame_set,
            self.commandIds['OPENSIM_CMD_debugpins_slot_toggle']     : self.bspDebugpins.cmd_slot_toggle,
            self.commandIds['OPENSIM_CMD_debugpins_slot_clr']        : self.bspDebugpins.cmd_slot_clr,
            self.commandIds['OPENSIM_CMD_debugpins_slot_set']        : self.bspDebugpins.cmd_slot_set,
            self.commandIds['OPENSIM_CMD_debugpins_fsm_toggle']      : self.bspDebugpins.cmd_fsm_toggle,
            self.commandIds['OPENSIM_CMD_debugpins_fsm_clr']         : self.bspDebugpins.cmd_fsm_clr,
            self.commandIds['OPENSIM_CMD_debugpins_fsm_set']         : self.bspDebugpins.cmd_fsm_set,
            self.commandIds['OPENSIM_CMD_debugpins_task_toggle']     : self.bspDebugpins.cmd_task_toggle,
            self.commandIds['OPENSIM_CMD_debugpins_task_clr']        : self.bspDebugpins.cmd_task_clr,
            self.commandIds['OPENSIM_CMD_debugpins_task_set']        : self.bspDebugpins.cmd_task_set,
            self.commandIds['OPENSIM_CMD_debugpins_isr_toggle']      : self.bspDebugpins.cmd_isr_toggle,
            self.commandIds['OPENSIM_CMD_debugpins_isr_clr']         : self.bspDebugpins.cmd_isr_clr,
            self.commandIds['OPENSIM_CMD_debugpins_isr_set']         : self.bspDebugpins.cmd_isr_set,
            self.commandIds['OPENSIM_CMD_debugpins_radio_toggle']    : self.bspDebugpins.cmd_radio_toggle,
            self.commandIds['OPENSIM_CMD_debugpins_radio_clr']       : self.bspDebugpins.cmd_radio_clr,
            self.commandIds['OPENSIM_CMD_debugpins_radio_set']       : self.bspDebugpins.cmd_radio_set,
            # eui64
            self.commandIds['OPENSIM_CMD_eui64_get']                 : self.bspEui64.cmd_get,
            # leds
            self.commandIds['OPENSIM_CMD_leds_init']                 : self.bspLeds.cmd_init,
            self.commandIds['OPENSIM_CMD_leds_error_on']             : self.bspLeds.cmd_error_on,
            self.commandIds['OPENSIM_CMD_leds_error_off']            : self.bspLeds.cmd_error_off,
            self.commandIds['OPENSIM_CMD_leds_error_toggle']         : self.bspLeds.cmd_error_toggle,
            self.commandIds['OPENSIM_CMD_leds_error_isOn']           : self.bspLeds.cmd_error_isOn,
            self.commandIds['OPENSIM_CMD_leds_radio_on']             : self.bspLeds.cmd_radio_on,
            self.commandIds['OPENSIM_CMD_leds_radio_off']            : self.bspLeds.cmd_radio_off,
            self.commandIds['OPENSIM_CMD_leds_radio_toggle']         : self.bspLeds.cmd_radio_toggle,
            self.commandIds['OPENSIM_CMD_leds_radio_isOn']           : self.bspLeds.cmd_radio_isOn,
            self.commandIds['OPENSIM_CMD_leds_sync_on']              : self.bspLeds.cmd_sync_on,
            self.commandIds['OPENSIM_CMD_leds_sync_off']             : self.bspLeds.cmd_sync_off,
            self.commandIds['OPENSIM_CMD_leds_sync_toggle']          : self.bspLeds.cmd_sync_toggle,
            self.commandIds['OPENSIM_CMD_leds_sync_isOn']            : self.bspLeds.cmd_sync_isOn,
            self.commandIds['OPENSIM_CMD_leds_debug_on']             : self.bspLeds.cmd_debug_on,
            self.commandIds['OPENSIM_CMD_leds_debug_off']            : self.bspLeds.cmd_debug_off,
            self.commandIds['OPENSIM_CMD_leds_debug_toggle']         : self.bspLeds.cmd_debug_toggle,
            self.commandIds['OPENSIM_CMD_leds_debug_isOn']           : self.bspLeds.cmd_debug_isOn,
            self.commandIds['OPENSIM_CMD_leds_all_on']               : self.bspLeds.cmd_all_on,
            self.commandIds['OPENSIM_CMD_leds_all_off']              : self.bspLeds.cmd_all_off,
            self.commandIds['OPENSIM_CMD_leds_all_toggle']           : self.bspLeds.cmd_all_toggle,
            self.commandIds['OPENSIM_CMD_leds_circular_shift']       : self.bspLeds.cmd_circular_shift,
            self.commandIds['OPENSIM_CMD_leds_increment']            : self.bspLeds.cmd_increment,
            # radio
            self.commandIds['OPENSIM_CMD_radio_init']                : self.bspRadio.cmd_init,
            self.commandIds['OPENSIM_CMD_radio_reset']               : self.bspRadio.cmd_reset,
            self.commandIds['OPENSIM_CMD_radio_startTimer']          : self.bspRadio.cmd_startTimer,
            self.commandIds['OPENSIM_CMD_radio_getTimerValue']       : self.bspRadio.cmd_getTimerValue,
            self.commandIds['OPENSIM_CMD_radio_setTimerPeriod']      : self.bspRadio.cmd_setTimerPeriod,
            self.commandIds['OPENSIM_CMD_radio_getTimerPeriod']      : self.bspRadio.cmd_getTimerPeriod,
            self.commandIds['OPENSIM_CMD_radio_setFrequency']        : self.bspRadio.cmd_setFrequency,
            self.commandIds['OPENSIM_CMD_radio_rfOn']                : self.bspRadio.cmd_rfOn,
            self.commandIds['OPENSIM_CMD_radio_rfOff']               : self.bspRadio.cmd_rfOff,
            self.commandIds['OPENSIM_CMD_radio_loadPacket']          : self.bspRadio.cmd_loadPacket,
            self.commandIds['OPENSIM_CMD_radio_txEnable']            : self.bspRadio.cmd_txEnable,
            self.commandIds['OPENSIM_CMD_radio_txNow']               : self.bspRadio.cmd_txNow,
            self.commandIds['OPENSIM_CMD_radio_rxEnable']            : self.bspRadio.cmd_rxEnable,
            self.commandIds['OPENSIM_CMD_radio_rxNow']               : self.bspRadio.cmd_rxNow,
            self.commandIds['OPENSIM_CMD_radio_getReceivedFrame']    : self.bspRadio.cmd_getReceivedFrame,
            # radiotimer
            self.commandIds['OPENSIM_CMD_radiotimer_init']           : self.bspRadiotimer.cmd_init,
            self.commandIds['OPENSIM_CMD_radiotimer_start']          : self.bspRadiotimer.cmd_start,
            self.commandIds['OPENSIM_CMD_radiotimer_getValue']       : self.bspRadiotimer.cmd_getValue,
            self.commandIds['OPENSIM_CMD_radiotimer_setPeriod']      : self.bspRadiotimer.cmd_setPeriod,
            self.commandIds['OPENSIM_CMD_radiotimer_getPeriod']      : self.bspRadiotimer.cmd_getPeriod,
            self.commandIds['OPENSIM_CMD_radiotimer_schedule']       : self.bspRadiotimer.cmd_schedule,
            self.commandIds['OPENSIM_CMD_radiotimer_cancel']         : self.bspRadiotimer.cmd_cancel,
            self.commandIds['OPENSIM_CMD_radiotimer_getCapturedTime']: self.bspRadiotimer.cmd_getCapturedTime,
            # uart
            self.commandIds['OPENSIM_CMD_uart_init']                 : self.bspUart.cmd_init,
            self.commandIds['OPENSIM_CMD_uart_enableInterrupts']     : self.bspUart.cmd_enableInterrupts,
            self.commandIds['OPENSIM_CMD_uart_disableInterrupts']    : self.bspUart.cmd_disableInterrupts,
            self.commandIds['OPENSIM_CMD_uart_clearRxInterrupts']    : self.bspUart.cmd_clearRxInterrupts,
            self.commandIds['OPENSIM_CMD_uart_clearTxInterrupts']    : self.bspUart.cmd_clearTxInterrupts,
            self.commandIds['OPENSIM_CMD_uart_writeByte']            : self.bspUart.cmd_writeByte,
            self.commandIds['OPENSIM_CMD_uart_readByte']             : self.bspUart.cmd_readByte,
        }
        # logging
        self.log   = logging.getLogger('MoteHandler')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('MoteHandler')
        
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
    
    def setId(self,id):
        self.id = id
    
    def setLocation(self,location):
        self.location = location
    
    def sendCommand(self,commandId,params=[]):
        
        # update statistics
        self.numTxCommands += 1
        
        # send command over connection
        dataToSend  = ''
        dataToSend += chr(commandId)
        for c in params:
            dataToSend += chr(c)
        self.conn.send(dataToSend)
    
    #======================== private =========================================
    
    def _handleReceivedCommand(self,input):
        
        # update statistics
        self.numRxCommands += 1
        
        # apply the delay
        self.engine.pauseOrDelay()
        
        # get the command id and params from the received command
        cmdId  = ord(input[0])
        #params = [ord(c) for c in input[1:]]
        params = input[1:]
        
        # make sure I know what callback to call
        assert(cmdId in self.commandCallbacks)
        
        # call the callback
        returnVal = self.commandCallbacks[cmdId](params)