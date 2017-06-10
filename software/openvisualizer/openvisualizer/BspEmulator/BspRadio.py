#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging

from openvisualizer.SimEngine     import SimEngine, \
                                         Propagation
from openvisualizer.eventBus      import eventBusClient
import BspModule

class RadioState:
    STOPPED             = 'STOPPED'              # Completely stopped.
    RFOFF               = 'RFOFF'                # Listening for commands by RF chain is off.
    SETTING_FREQUENCY   = 'SETTING_FREQUENCY'    # Configuring the frequency.
    FREQUENCY_SET       = 'FREQUENCY_SET'        # Done configuring the frequency.
    LOADING_PACKET      = 'LOADING_PACKET'       # Loading packet to send over SPI.
    PACKET_LOADED       = 'PACKET_LOADED'        # Packet is loaded in the TX buffer.
    ENABLING_TX         = 'ENABLING_TX'          # The RF Tx chaing is being enabled (includes locked the PLL).
    TX_ENABLED          = 'TX_ENABLED'           # Radio completely ready to transmit.
    TRANSMITTING        = 'TRANSMITTING'         # Busy transmitting bytes.
    ENABLING_RX         = 'ENABLING_RX'          # The RF Rx chaing is being enabled (includes locked the PLL).
    LISTENING           = 'LISTENING'            # RF chain is on, listening, but no packet received yet.
    RECEIVING           = 'RECEIVING'            # Busy receiving bytes.
    TXRX_DONE           = 'TXRX_DONE'            # Frame has been sent/received completely.
    TURNING_OFF         = 'TURNING_OFF'          # Turning the RF chain off.

class BspRadio(BspModule.BspModule,eventBusClient.eventBusClient):
    '''
    Emulates the 'radio' BSP module
    '''
    
    INTR_STARTOFFRAME_MOTE        = 'radio.startofframe_fromMote'
    INTR_ENDOFFRAME_MOTE          = 'radio.endofframe_fromMote'
    INTR_STARTOFFRAME_PROPAGATION = 'radio.startofframe_fromPropagation'
    INTR_ENDOFFRAME_PROPAGATION   = 'radio.endofframe_fromPropagation'
    
    def __init__(self,motehandler):
        
        # store params
        self.engine      = SimEngine.SimEngine()
        self.motehandler = motehandler
        
        # local variables
        self.timeline    = self.engine.timeline
        self.propagation = self.engine.propagation
        self.sctimer     = self.motehandler.bspSctimer
        
        # local variables
        self.frequency   = None   # frequency the radio is tuned to
        self.isRfOn      = False  # radio is off
        self.txBuf       = []
        self.rxBuf       = []
        self.delayTx     = 0.000214
        
        # initialize the parents
        BspModule.BspModule.__init__(self,'BspRadio')
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'BspRadio_{0}'.format(self.motehandler.getId()),
            registrations         =  [],
        )
        
        # set initial state
        self._changeState(RadioState.STOPPED)
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self):
        '''emulates
           void radio_init()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_init')
        
        # change state
        self._changeState(RadioState.STOPPED)
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # change state
        self._changeState(RadioState.RFOFF)
    
    def cmd_reset(self):
        '''emulates
           void radio_reset()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_reset')
        
        # change state
        self._changeState(RadioState.STOPPED)
    
    def cmd_setFrequency(self,frequency):
        '''emulates
           void radio_setFrequency(uint8_t frequency)'''
        
        # store params
        self.frequency   = frequency
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_setFrequency frequency='+str(self.frequency))
        
        # change state
        self._changeState(RadioState.SETTING_FREQUENCY)
        
        # change state
        self._changeState(RadioState.FREQUENCY_SET)
    
    def cmd_rfOn(self):
        '''emulates
           void radio_rfOn()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_rfOn')
        
        # update local variable
        self.isRfOn = True
    
    def cmd_rfOff(self):
        '''emulates
           void radio_rfOff()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_rfOff')
        
        # change state
        self._changeState(RadioState.TURNING_OFF)
        
        # update local variable
        self.isRfOn = False
        
        # change state
        self._changeState(RadioState.RFOFF)
        
        # wiggle de debugpin
        self.motehandler.bspDebugpins.cmd_radio_clr()
    
    def cmd_loadPacket(self,packetToLoad):
        '''emulates
           void radio_loadPacket(uint8_t* packet, uint8_t len)'''
        
        # make sure length of params is expected
        assert(len(packetToLoad)<=127)
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_loadPacket len={0}'.format(len(packetToLoad)))
        
        # change state
        self._changeState(RadioState.LOADING_PACKET)
        
        # update local variable
        self.txBuf = [len(packetToLoad)]+packetToLoad
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('txBuf={0}'.format(self.txBuf))
        
        # change state
        self._changeState(RadioState.PACKET_LOADED)
    
    def cmd_txEnable(self):
        '''emulates
           void radio_txEnable()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_txEnable')
        
        # change state
        self._changeState(RadioState.ENABLING_TX)
        
        # change state
        self._changeState(RadioState.TX_ENABLED)
        
        # wiggle de debugpin
        self.motehandler.bspDebugpins.cmd_radio_set()
    
    def cmd_txNow(self):
        '''emulates
           void radio_txNow()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_txNow')
        
        # change state
        self._changeState(RadioState.TRANSMITTING)
        
        # get current time
        currenttime          = self.timeline.getCurrentTime()
        
        # calculate when the "start of frame" event will take place
        startOfFrameTime     = currenttime+self.delayTx
        
        # schedule "start of frame" event
        self.timeline.scheduleEvent(startOfFrameTime,
                                    self.motehandler.getId(),
                                    self.intr_startOfFrame_fromMote,
                                    self.INTR_STARTOFFRAME_MOTE)
    
    def cmd_rxEnable(self):
        '''emulates
           void radio_rxEnable()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_rxEnable')
        
        # change state
        self._changeState(RadioState.ENABLING_RX)
        
        # change state
        self._changeState(RadioState.LISTENING)
        
        # wiggle de debugpin
        self.motehandler.bspDebugpins.cmd_radio_set()
    
    def cmd_rxNow(self):
        '''emulates
           void radio_rxNow()'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_rxNow')
        
        # change state
        self._changeState(RadioState.LISTENING)
    
    def cmd_getReceivedFrame(self):
        '''emulates
           void radio_getReceivedFrame(
           uint8_t* pBufRead,
           uint8_t* pLenRead,
           uint8_t  maxBufLen,
           int8_t*  pRssi,
           uint8_t* pLqi,
           uint8_t* pCrc)'''
        
        # log the activity
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('cmd_getReceivedFrame')
        
        #==== prepare response
        rxBuffer   = self.rxBuf[1:]
        rssi       = self.rssi
        lqi        = self.lqi
        crc        = self.crcPasses
        
        # respond
        return rxBuffer, rssi, lqi, crc
    
    #======================== interrupts ======================================
    
    def intr_startOfFrame_fromMote(self):
        
        # indicate transmission starts on eventBus
        self.dispatch(          
            signal           = Propagation.Propagation.SIGNAL_WIRELESSTXSTART,
            data             = (self.motehandler.getId(),self.txBuf,self.frequency)
        )
        
        # schedule the "end of frame" event
        currentTime          = self.timeline.getCurrentTime()
        endOfFrameTime       = currentTime+self._packetLengthToDuration(len(self.txBuf))
        self.timeline.scheduleEvent(
            endOfFrameTime,
            self.motehandler.getId(),
            self.intr_endOfFrame_fromMote,
            self.INTR_ENDOFFRAME_MOTE,
        )
        
        # signal start of frame to mote
        counterVal           = self.sctimer.cmd_readCounter()
        
        # indicate to the mote
        self.motehandler.mote.radio_isr_startFrame(counterVal)
        
        # kick the scheduler
        return True
    
    def intr_startOfFrame_fromPropagation(self):
        
        # signal start of frame to mote
        counterVal           = self.sctimer.cmd_readCounter()
        
        # indicate to the mote
        self.motehandler.mote.radio_isr_startFrame(counterVal)
        
        # do NOT kick the scheduler
        return True
    
    def intr_endOfFrame_fromMote(self):
        
        # indicate transmission ends on eventBus
        self.dispatch(          
            signal           = Propagation.Propagation.SIGNAL_WIRELESSTXEND,
            data             = self.motehandler.getId(),
        )
        
        # signal end of frame to mote
        counterVal           = self.sctimer.cmd_readCounter()
        
        # indicate to the mote
        self.motehandler.mote.radio_isr_endFrame(counterVal)
        
        # kick the scheduler
        return True
    
    def intr_endOfFrame_fromPropagation(self):
        
        # signal end of frame to mote
        counterVal           = self.sctimer.cmd_readCounter()
        
        # log
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('intr_endOfFrame_fromPropagation counterVal={0}'.format(counterVal))
        
        # indicate to the mote
        self.motehandler.mote.radio_isr_endFrame(counterVal)
        
        # do NOT kick the scheduler
        return True
    
    #======================== indication from Propagation =====================
    
    def indicateTxStart(self,moteId,packet,channel):
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('_indicateTxStart from moteId={0} channel={1} len={2}'.format(moteId,channel,len(packet)))
    
        if (self.isInitialized==True         and
            self.state==RadioState.LISTENING and
            self.frequency==channel):
            self._changeState(RadioState.RECEIVING)
            self.rxBuf       = packet
            self.rssi        = -50
            self.lqi         = 100
            self.crcPasses   = True
            
            # log
            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('rxBuf={0}'.format(self.rxBuf))
            
            # schedule start of frame
            self.timeline.scheduleEvent(
                self.timeline.getCurrentTime(),
                self.motehandler.getId(),
                self.intr_startOfFrame_fromPropagation,
                self.INTR_STARTOFFRAME_PROPAGATION,
            )
    
    def indicateTxEnd(self,moteId):
        
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('_indicateTxEnd from moteId={0}'.format(moteId))
        
        if (self.isInitialized==True and
            self.state==RadioState.RECEIVING):
            self._changeState(RadioState.LISTENING)
            
            # schedule end of frame
            self.timeline.scheduleEvent(
                self.timeline.getCurrentTime(),
                self.motehandler.getId(),
                self.intr_endOfFrame_fromPropagation,
                self.INTR_ENDOFFRAME_PROPAGATION,
            )
    
    #======================== private =========================================
    
    def _packetLengthToDuration(self,numBytes):
        return float(numBytes*8)/250000.0
        
    def _changeState(self,newState):
        self.state = newState
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug('state={0}'.format(self.state))