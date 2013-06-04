#!/usr/bin/python

import logging
import threading

import BspModule

class BspUart(BspModule.BspModule):
    '''
    \brief Emulates the 'uart' BSP module
    '''
    
    INTR_TX   = 'uart.tx'
    INTR_RX   = 'uart.rx'
    BAUDRATE  = 115200
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine               = engine
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
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspUart')
    
    #======================== public ==========================================
    
    #=== interact with UART
    
    def read(self,numBytesToRead):
        assert numBytesToRead==1
        
        # wait for something to appear in the RX buffer
        self.uartRxBufferSem.acquire()
        
        # pop the first element
        with self.uartRxBufferLock:
            assert len(self.uartRxBuffer)>0
            returnVal = chr(self.uartRxBuffer.pop(0))
        
        # return that element
        return returnVal
    
    def write(self,byteToWrite):
        print 'poipoipoipoipoipoipoi TODO write'
    
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
        
    def cmd_readByte(self,params):
        '''emulates
           uint8_t uart_readByte()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_readByte')
        
        raise NotImplementedError()
    
    #======================== interrupts ======================================
    
    def intr_tx(self):
        '''
        \brief Done is done sending a byte over the UART.
        '''
        
        # send interrupt to mote
        self.motehandler.mote.uart_isr_tx()
        
        # do *not* kick the scheduler
        return False
    
    
    def intr_rx(self):
        '''
        \brief The mote received a byte from the UART.
        '''
        
        # send interrupt to mote
        self.motehandler.mote.uart_isr_rx()
        
        # do *not* kick the scheduler
        return False
    
    #======================== private =========================================
    
    