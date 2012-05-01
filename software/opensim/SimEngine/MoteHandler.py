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

TCPRXBUFSIZE       = 4096    # size of the TCP reception buffer

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class MoteHandler(threading.Thread):
    '''
    \brief Handle the connection of a mote.
    '''
    
    def __init__(self,engine,conn,addr,port):
        
        # store params
        self.engine               = engine
        self.conn                 = conn
        self.addr                 = addr
        self.port                 = port
        
        # local variables
        self.waitingForReplySem   = threading.Lock()
        self.waitingForReply      = False
        self.bspBoard             = BspBoard.BspBoard()
        self.bspBsp_timer         = BspBsp_timer.BspBsp_timer()
        self.bspDebugpins         = BspDebugpins.BspDebugpins()
        self.bspEui64             = BspEui64.BspEui64()
        self.bspLeds              = BspLeds.BspLeds()
        self.bspRadio             = BspRadio.BspRadio()
        self.bspRadiotimer        = BspRadiotimer.BspRadiotimer()
        self.bspUart              = BspUart.BspUart()
        self.commandCallbacks = {
            # board
            0 : self.bspBoard.cmd_init,
            1 : self.bspBoard.cmd_sleep,
            # bsp_timer
            2 : self.bspBsp_timer.cmd_init,
            3 : self.bspBsp_timer.cmd_reset,
            4 : self.bspBsp_timer.cmd_scheduleIn,
            5 : self.bspBsp_timer.cmd_cancel_schedule,
            # debugpins
            6 : self.bspDebugpins.cmd_init,
            7 : self.bspDebugpins.cmd_frame_toggle,
            8 : self.bspDebugpins.cmd_frame_clr,
            9 : self.bspDebugpins.cmd_frame_set,
            10: self.bspDebugpins.cmd_slot_toggle,
            11: self.bspDebugpins.cmd_slot_clr,
            12: self.bspDebugpins.cmd_slot_set,
            13: self.bspDebugpins.cmd_fsm_toggle,
            14: self.bspDebugpins.cmd_fsm_clr,
            15: self.bspDebugpins.cmd_fsm_set,
            16: self.bspDebugpins.cmd_task_toggle,
            17: self.bspDebugpins.cmd_task_clr,
            18: self.bspDebugpins.cmd_task_set,
            19: self.bspDebugpins.cmd_isr_toggle,
            20: self.bspDebugpins.cmd_isr_clr,
            21: self.bspDebugpins.cmd_isr_set,
            22: self.bspDebugpins.cmd_radio_toggle,
            23: self.bspDebugpins.cmd_radio_clr,
            24: self.bspDebugpins.cmd_radio_set,
            # eui64
            25: self.bspEui64.cmd_get,
            # leds
            26: self.bspLeds.cmd_init,
            27: self.bspLeds.cmd_error_on,
            28: self.bspLeds.cmd_error_off,
            29: self.bspLeds.cmd_error_toggle,
            30: self.bspLeds.cmd_error_isOn,
            31: self.bspLeds.cmd_radio_on,
            32: self.bspLeds.cmd_radio_off,
            33: self.bspLeds.cmd_radio_toggle,
            34: self.bspLeds.cmd_radio_isOn,
            35: self.bspLeds.cmd_sync_on,
            36: self.bspLeds.cmd_sync_off,
            37: self.bspLeds.cmd_sync_toggle,
            38: self.bspLeds.cmd_sync_isOn,
            39: self.bspLeds.cmd_debug_on,
            40: self.bspLeds.cmd_debug_off,
            41: self.bspLeds.cmd_debug_toggle,
            42: self.bspLeds.cmd_debug_isOn,
            43: self.bspLeds.cmd_all_on,
            44: self.bspLeds.cmd_all_off,
            45: self.bspLeds.cmd_all_toggle,
            46: self.bspLeds.cmd_circular_shift,
            47: self.bspLeds.cmd_increment,
            # radio
            48: self.bspRadio.cmd_init,
            49: self.bspRadio.cmd_reset,
            50: self.bspRadio.cmd_startTimer,
            51: self.bspRadio.cmd_getTimerValue,
            52: self.bspRadio.cmd_setTimerPeriod,
            53: self.bspRadio.cmd_getTimerPeriod,
            54: self.bspRadio.cmd_setFrequency,
            55: self.bspRadio.cmd_rfOn,
            56: self.bspRadio.cmd_rfOff,
            57: self.bspRadio.cmd_loadPacket,
            58: self.bspRadio.cmd_txEnable,
            59: self.bspRadio.cmd_txNow,
            60: self.bspRadio.cmd_rxEnable,
            61: self.bspRadio.cmd_rxNow,
            62: self.bspRadio.cmd_getReceivedFrame,
            # radiotimer
            63: self.bspRadiotimer.cmd_init,
            64: self.bspRadiotimer.cmd_start,
            65: self.bspRadiotimer.cmd_getValue,
            66: self.bspRadiotimer.cmd_setPeriod,
            67: self.bspRadiotimer.cmd_getPeriod,
            68: self.bspRadiotimer.cmd_schedule,
            69: self.bspRadiotimer.cmd_cancel,
            70: self.bspRadiotimer.cmd_getCapturedTime,
            # uart
            71: self.bspUart.cmd_init,
            72: self.bspUart.cmd_enableInterrupts,
            73: self.bspUart.cmd_disableInterrupts,
            74: self.bspUart.cmd_clearRxInterrupts,
            75: self.bspUart.cmd_clearTxInterrupts,
            76: self.bspUart.cmd_writeByte,
            77: self.bspUart.cmd_readByte,
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
            try:
                input = self.conn.recv(TCPRXBUFSIZE)
            except socket.error as err:
                self.log.critical('connection error (err='+str(err)+')')
                break
            
            self.log.info('received input='+str(ord(input[0])))
            if self.waitingForReply:
                self.log.debug('This is a reply.')
                self.response = input
                self.waitingForReplySem.release()
            else:
                self.log.debug('This is a response.')
                self._handleReceivedCommand(input)
    
    #======================== public ==========================================
    
    def sendCommand(send,dataToSend):
        self.conn.send(dataToSend)
        self.waitingForReply = True
        self.waitingForReplySem.acquire()
    
    #======================== private =========================================
    
    def _handleReceivedCommand(self,input):
        
        # apply the delay
        self.engine.pauseOrDelay()
        
        # get the command id from the received command
        cmdId = ord(input[0])
        
        # make sure I know what callback to call
        assert(cmdId in self.commandCallbacks)
        
        # call the callback
        returnVal = self.commandCallbacks[cmdId]()
        
        # if the called function didn't return anything, assume return OK
        if not returnVal:
            returnVal = 0
        
        # send back the value returned by the callback
        self.conn.send(chr(returnVal))