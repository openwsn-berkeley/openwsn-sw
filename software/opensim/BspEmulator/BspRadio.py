#!/usr/bin/python

import struct
import BspModule

class RadioState:
    STOPPED             = 'STOPPED',             # Completely stopped.
    RFOFF               = 'RFOFF',               # Listening for commands by RF chain is off.
    SETTING_FREQUENCY   = 'SETTING_FREQUENCY',   # Configuring the frequency.
    FREQUENCY_SET       = 'FREQUENCY_SET',       # Done configuring the frequency.
    LOADING_PACKET      = 'LOADING_PACKET',      # Loading packet to send over SPI.
    PACKET_LOADED       = 'PACKET_LOADED',       # Packet is loaded in the TX buffer.
    ENABLING_TX         = 'ENABLING_TX',         # The RF Tx chaing is being enabled (includes locked the PLL).
    TX_ENABLED          = 'TX_ENABLED',          # Radio completely ready to transmit.
    TRANSMITTING        = 'TRANSMITTING',        # Busy transmitting bytes.
    ENABLING_RX         = 'ENABLING_RX',         # The RF Rx chaing is being enabled (includes locked the PLL).
    LISTENING           = 'LISTENING',           # RF chain is on, listening, but no packet received yet.
    RECEIVING           = 'RECEIVING',           # Busy receiving bytes.
    TXRX_DONE           = 'TXRX_DONE',           # Frame has been sent/received completely.
    TURNING_OFF         = 'TURNING_OFF',         # Turning the RF chain off.

class BspRadio(BspModule.BspModule):
    '''
    \brief Emulates the 'radio' BSP module
    '''
    
    INTR_STARTOFFRAME = 'radio.startofframe'
    INTR_ENDOFFRAME   = 'radio.endofframe'
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine      = engine
        self.motehandler = motehandler
        
        # local variables
        self.timeline    = self.engine.timeline
        self.propagation = self.engine.propagation
        self.radiotimer  = self.motehandler.bspRadiotimer
        
        # local variables
        self.state       = RadioState.STOPPED
        self.frequency   = None   # frequency the radio is tuned to
        self.isRfOn      = False  # radio is off
        self.txBuf       = []
        self.rxBuf       = []
        self.delayTx     = 0.000214
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadio')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        '''emulates
           void radio_init()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_init')
        
        # change state
        self.state         = RadioState.STOPPED
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # change state
        self.state         = RadioState.RFOFF
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_init'])
    
    def cmd_reset(self,params):
        '''emulates
           void radio_reset()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_reset')
        
        # change state
        self.state         = RadioState.STOPPED
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_reset'])
    
    def cmd_startTimer(self,params):
        '''emulates
           void radio_startTimer(PORT_TIMER_WIDTH period)'''
        
        # log the activity
        self.log.debug('cmd_startTimer')
        
        # defer to radiotimer emulated BSPc(which sends answer)
        self.motehandler.bspRadiotimer.cmd_start(params)
    
    def cmd_getTimerValue(self,params):
        '''emulates
           PORT_TIMER_WIDTH radio_getTimerValue()'''
        
        # log the activity
        self.log.debug('cmd_getTimerValue')
        
        # defer to radiotimer emulated BSPc(which sends answer)
        self.motehandler.bspRadiotimer.cmd_getValue(params)
    
    def cmd_setTimerPeriod(self,params):
        '''emulates
           void radio_setTimerPeriod(PORT_TIMER_WIDTH period)'''
        
        # log the activity
        self.log.debug('cmd_setTimerPeriod')
        
        # defer to radiotimer emulated BSPc(which sends answer)
        self.motehandler.bspRadiotimer.cmd_setPeriod(params)
    
    def cmd_getTimerPeriod(self,params):
        '''emulates
           PORT_TIMER_WIDTH radio_getTimerPeriod()'''
        
        # log the activity
        self.log.debug('cmd_getTimerPeriod')
        
        # defer to radiotimer emulated BSPc(which sends answer)
        self.motehandler.bspRadiotimer.cmd_getPeriod(params)
    
    def cmd_setFrequency(self,params):
        '''emulates
           void radio_setFrequency(uint8_t frequency)'''
        
        # unpack the parameters
        (self.frequency,)            = struct.unpack('B', params)
        
        # log the activity
        self.log.debug('cmd_setFrequency frequency='+str(self.frequency))
        
        # change state
        self.state         = RadioState.SETTING_FREQUENCY
        
        # change state
        self.state         = RadioState.FREQUENCY_SET
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_setFrequency'])
    
    def cmd_rfOn(self,params):
        '''emulates
           void radio_rfOn()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_rfOn')
        
        # update local variable
        self.isRfOn = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rfOn'])
    
    def cmd_rfOff(self,params):
        '''emulates
           void radio_rfOff()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_rfOff')
        
        # change state
        self.state         = RadioState.TURNING_OFF
        
        # update local variable
        self.isRfOn = False
        
        # change state
        self.state         = RadioState.RFOFF
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rfOff'])
    
    def cmd_loadPacket(self,params):
        '''emulates
           void radio_loadPacket(uint8_t* packet, uint8_t len)'''
        
        # log the activity
        self.log.debug('cmd_loadPacket')
        
        # change state
        self.state         = RadioState.LOADING_PACKET
        
        # update local variable
        self.txBuf = []
        for c in params:
            self.txBuf.append(ord(c))
        
        # change state
        self.state         = RadioState.PACKET_LOADED
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_loadPacket'])
    
    def cmd_txEnable(self,params):
        '''emulates
           void radio_txEnable()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_txEnable')
        
        # change state
        self.state         = RadioState.ENABLING_TX
        
        # change state
        self.state         = RadioState.TX_ENABLED
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_txEnable'])
    
    def cmd_txNow(self,params):
        '''emulates
           void radio_txNow()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_txNow')
        
        # change state
        self.state           = RadioState.TRANSMITTING
        
        # get current time
        currenttime          = self.timeline.getCurrentTime()
        
        # calculate when the "start of frame" event will take place
        startOfFrameTime     = currenttime+self.delayTx
        
        # schedule "start of frame" event
        self.timeline.scheduleEvent(startOfFrameTime,
                                    self.motehandler.getId(),
                                    self.intr_startOfFrame,
                                    self.INTR_STARTOFFRAME)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_txNow'])
    
    def cmd_rxEnable(self,params):
        '''emulates
           void radio_rxEnable()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_rxEnable')
        
        # change state
        self.state         = RadioState.ENABLING_RX
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rxEnable'])
    
    def cmd_rxNow(self,params):
        '''emulates
           void radio_rxNow()'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_rxNow')
        
        # change state
        self.state         = RadioState.LISTENING
    
    def cmd_getReceivedFrame(self,params):
        '''emulates
           void radio_getReceivedFrame(uint8_t* pBufRead,
                                       uint8_t* pLenRead,
                                       uint8_t  maxBufLen,
                                        int8_t* pRssi,
                                       uint8_t* pLqi,
                                       uint8_t* pCrc)'''
        
        # log the activity
        self.log.debug('cmd_getReceivedFrame')
        
        raise NotImplementedError()
    
    #======================== interrupts ======================================
    
    def intr_startOfFrame(self):
        
        # indicate transmission starts to propagation model
        self.propagation.txStart(self.motehandler.getId(),
                                 self.txBuf,
                                 self.frequency)
        
        
        # schedule the "end of frame" event
        currentTime          = self.timeline.getCurrentTime()
        endOfFrameTime       = currentTime+self._packetLengthToDuration(len(self.txBuf))
        self.timeline.scheduleEvent(endOfFrameTime,
                                    self.motehandler.getId(),
                                    self.intr_endOfFrame,
                                    self.INTR_ENDOFFRAME)
        
        # signal start of frame to mote
        counterVal           = self.radiotimer.getCounterVal()
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_isr_startFrame'],
                                     [(counterVal>>0)%0xff,(counterVal>>8)%0xff])
    
    def intr_endOfFrame(self):
        # indicate transmission end to propagation model
        self.propagation.txEnd(self.motehandler.getId())
        
        # signal start of frame to mote
        counterVal           = self.radiotimer.getCounterVal()
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_isr_endFrame'],
                                     [(counterVal>>0)%0xff,(counterVal>>8)%0xff])
    
    #======================== private =========================================
    
    def _packetLengthToDuration(self,numBytes):
        return float(numBytes*8)/250000.0