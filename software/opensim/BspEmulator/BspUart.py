#!/usr/bin/python

import struct
import BspModule
import serial

class BspUart(BspModule.BspModule):
    '''
    \brief Emulates the 'uart' BSP module
    '''
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine               = engine
        self.motehandler          = motehandler
        
        # local variables
        #self.serialHandler        = serial.Serial('\\\\.\\CNCA0',baudrate=115200)
        self.interruptsEnabled    = False
        self.txInterruptFlag      = False
        self.rxInterruptFlag      = False
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspUart')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        '''emulates
           void uart_init()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_init'])
    
    def cmd_enableInterrupts(self,params):
        '''emulates
           void uart_enableInterrupts()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_enableInterrupts')
        
        # update variables
        self.interruptsEnabled    = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_enableInterrupts'])
    
    def cmd_disableInterrupts(self,params):
        '''emulates
           void uart_disableInterrupts()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_disableInterrupts')
        
        # update variables
        self.interruptsEnabled    = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_disableInterrupts'])
    
    def cmd_clearRxInterrupts(self,params):
        '''emulates
           void uart_clearRxInterrupts()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_clearRxInterrupts')
        
        # update variables
        self.rxInterruptFlag      = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_clearRxInterrupts'])
    
    def cmd_clearTxInterrupts(self,params):
        '''emulates
           void uart_clearTxInterrupts()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_clearTxInterrupts')
        
        # update variables
        self.txInterruptFlag      = False
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_clearTxInterrupts'])
    
    def cmd_writeByte(self,params):
        '''emulates
           void uart_writeByte(uint8_t byteToWrite)'''
        
        # unpack the parameters
        (self.lastTxChar,)        = struct.unpack('<c', params)
        
        # log the activity
        self.log.debug('cmd_writeByte lastTxChar='+str(self.lastTxChar))
        
        # write to serial port
        #self.serialHandler.write(self.lastTxChar)
        
        # set tx interrupt flag
        self.txInterruptFlag      = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_uart_writeByte'])
    
    def cmd_readByte(self,params):
        '''emulates
           uint8_t uart_readByte()'''
        
        # log the activity
        self.log.debug('cmd_readByte')
        
        raise NotImplementedError()
    
    #======================== private =========================================