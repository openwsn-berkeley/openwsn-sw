#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
import threading

from openvisualizer.SimEngine     import SimEngine
import BspModule

class BspUart(BspModule.BspModule):
    '''
    Emulates the 'uart' BSP module
    '''
    
    INTR_TX   = 'uart.tx'
    INTR_RX   = 'uart.rx'
    BAUDRATE  = 115200
    
    def __init__(self,motehandler):
        
        # store params
        self.engine               = SimEngine.SimEngine()
        self.motehandler          = motehandler
        
        # local variables
        self.timeline             = self.engine.timeline
        self.interruptsEnabled    = False
        self.txInterruptFlag      = False
        self.rxInterruptFlag      = False
        self.uartRxBuffer         = []
        self.uartRxBufferSem      = threading.Semaphore()
        self.uartRxBufferSem.acquire()
        self.uartRxBufferLock     = threading.Lock()
        self.uartTxBuffer         = []                # the bytes to be sent over UART
        self.uartTxNext           = None              # the byte that was just signaled to mote
        self.uartTxBufferLock     = threading.Lock()
        self.waitForDoneReading   = threading.Lock()
        self.waitForDoneReading.acquire()
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspUart')
    
    #======================== public ==========================================
    
    #=== interact with UART
    
    def read(self):
        '''
        Read a byte from the mote.
        '''
        
        # wait for something to appear in the RX buffer
        self.uartRxBufferSem.acquire()
        
        # copy uartRxBuffer
        with self.uartRxBufferLock:
            assert len(self.uartRxBuffer)>0
            returnVal             = [chr(b) for b in self.uartRxBuffer]
            self.uartRxBuffer     = []
        
        # return that element
        return returnVal
    
    def write(self,bytesToWrite):
        '''
        Write a string of bytes to the mote.
        '''
        
        assert len(bytesToWrite)
        
        with self.uartTxBufferLock:
            self.uartTxBuffer     = [ord(b) for b in bytesToWrite]
        
        self.engine.pause()
        self._scheduleNextTx()
        self.engine.resume()
    
    def doneReading(self):
        self.waitForDoneReading.release()
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void uart_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
    
    def cmd_enableInterrupts(self):
        '''emulates
           void uart_enableInterrupts()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_enableInterrupts')
        
        # update variables
        self.interruptsEnabled    = True
    
    def cmd_disableInterrupts(self):
        '''emulates
           void uart_disableInterrupts()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_disableInterrupts')
        
        # update variables
        self.interruptsEnabled    = False
    
    def cmd_clearRxInterrupts(self):
        '''emulates
           void uart_clearRxInterrupts()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_clearRxInterrupts')
        
        # update variables
        self.rxInterruptFlag      = False
    
    def cmd_clearTxInterrupts(self):
        '''emulates
           void uart_clearTxInterrupts()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_clearTxInterrupts')
        
        # update variables
        self.txInterruptFlag      = False
    
    def cmd_writeByte(self,byteToWrite):
        '''emulates
           void uart_writeByte(uint8_t byteToWrite)'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_writeByte byteToWrite='+str(self.byteToWrite))
        
        # set tx interrupt flag
        self.txInterruptFlag      = True
        
        # calculate the time at which the byte will have been sent
        doneSendingTime           = self.timeline.getCurrentTime()+float(1.0/float(self.BAUDRATE))
        
        # schedule uart TX interrupt in 1/BAUDRATE seconds
        self.timeline.scheduleEvent(
            doneSendingTime,
            self.motehandler.getId(),
            self.intr_tx,
            self.INTR_TX
        )
        
        # add to receive buffer
        with self.uartRxBufferLock:
            self.uartRxBuffer    += [byteToWrite]
        
        # release the semaphore indicating there is something in RX buffer
        self.uartRxBufferSem.release()
        
        # wait for the moteProbe to be done reading
        self.waitForDoneReading.acquire()
    
    def cmd_writeCircularBuffer_FASTSIM(self,buffer):
        '''emulates
           void uart_writeCircularBuffer_FASTSIM(uint8_t* buffer, uint8_t len)'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_writeCircularBuffer_FASTSIM buffer='+str(buffer))
        
        self._writeBuffer(buffer)
    
    def uart_writeBufferByLen_FASTSIM(self,buffer):
        '''emulates
           void uart_writeBufferByLen_FASTSIM(uint8_t* buffer, uint8_t len)'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('uart_writeBufferByLen_FASTSIM buffer='+str(buffer))
        
        self._writeBuffer(buffer)
    
    def _writeBuffer(self,buffer):
        # set tx interrupt flag
        self.txInterruptFlag      = True
        
        # calculate the time at which the buffer will have been sent
        doneSendingTime           = self.timeline.getCurrentTime()+float(float(len(buffer))/float(self.BAUDRATE))
        
        # schedule uart TX interrupt in len(buffer)/BAUDRATE seconds
        self.timeline.scheduleEvent(
            doneSendingTime,
            self.motehandler.getId(),
            self.intr_tx,
            self.INTR_TX
        )
        
        # add to receive buffer
        with self.uartRxBufferLock:
            self.uartRxBuffer    += buffer
        
        # release the semaphore indicating there is something in RX buffer
        self.uartRxBufferSem.release()
        
        # wait for the moteProbe to be done reading
        self.waitForDoneReading.acquire()
    
    def cmd_readByte(self):
        '''emulates
           uint8_t uart_readByte()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_readByte')
        
        # retrieve the byte last sent
        with self.uartTxBufferLock:
            return self.uartTxNext
    
    #======================== interrupts ======================================
    
    def intr_tx(self):
        '''
        Mote is done sending a byte over the UART.
        '''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('intr_tx')
        
        # send interrupt to mote
        self.motehandler.mote.uart_isr_tx()
        
        # do *not* kick the scheduler
        return False
    
    def intr_rx(self):
        '''
        Interrupt to indicate to mote it received a byte from the UART.
        '''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('intr_rx')
        
        with self.uartTxBufferLock:
            
            # make sure there is a byte to TX
            assert len(self.uartTxBuffer)
            
            # get the byte that is being transmitted
            self.uartTxNext  = self.uartTxBuffer.pop(0)
            
            # schedule the next interrupt, if any bytes left
            if len(self.uartTxBuffer):
                self._scheduleNextTx()
        
        # send RX interrupt to mote
        self.motehandler.mote.uart_isr_rx()
        
        # do *not* kick the scheduler
        return False
    
    #======================== private =========================================
    
    def _scheduleNextTx(self):
        
        # calculate time at which byte will get out
        timeNextTx           = self.timeline.getCurrentTime()+float(1.0/float(self.BAUDRATE))
        
        # schedule that event
        self.timeline.scheduleEvent(
            timeNextTx,
            self.motehandler.getId(),
            self.intr_rx,
            self.INTR_RX
        )
    
    