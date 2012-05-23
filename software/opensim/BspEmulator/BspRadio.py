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
    
    INTR_STARTOFFRAME_MOTE        = 'radio.startofframe_fromMote'
    INTR_ENDOFFRAME_MOTE          = 'radio.endofframe_fromMote'
    INTR_STARTOFFRAME_PROPAGATION = 'radio.startofframe_fromPropagation'
    INTR_ENDOFFRAME_PROPAGATION   = 'radio.endofframe_fromPropagation'
    
    def __init__(self,engine,motehandler):
        
        # store params
        self.engine      = engine
        self.motehandler = motehandler
        
        # local variables
        self.timeline    = self.engine.timeline
        self.propagation = self.engine.propagation
        self.radiotimer  = self.motehandler.bspRadiotimer
        
        # local variables
        self.frequency   = None   # frequency the radio is tuned to
        self.isRfOn      = False  # radio is off
        self.txBuf       = []
        self.rxBuf       = []
        self.delayTx     = 0.000214
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadio')
        
        # set initial state
        self._changeState(RadioState.STOPPED)
    
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
        self._changeState(RadioState.STOPPED)
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # change state
        self._changeState(RadioState.RFOFF)
        
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
        self._changeState(RadioState.STOPPED)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_reset'])
    
    def cmd_startTimer(self,params):
        '''emulates
           void radio_startTimer(PORT_TIMER_WIDTH period)'''
        
        # log the activity
        self.log.debug('cmd_startTimer')
        
        # defer to radiotimer
        params = self.motehandler.bspRadiotimer.cmd_start(params,True)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_startTimer'],
                                     params)
    
    def cmd_getTimerValue(self,params):
        '''emulates
           PORT_TIMER_WIDTH radio_getTimerValue()'''
        
        # log the activity
        self.log.debug('cmd_getTimerValue')
        
        # defer to radiotimer
        params = self.motehandler.bspRadiotimer.cmd_getValue(params,True)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_getTimerValue'],
                                     params)
    
    def cmd_setTimerPeriod(self,params):
        '''emulates
           void radio_setTimerPeriod(PORT_TIMER_WIDTH period)'''
        
        # log the activity
        self.log.debug('cmd_setTimerPeriod')
        
        # defer to radiotimer
        params = self.motehandler.bspRadiotimer.cmd_setPeriod(params,True)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_setTimerPeriod'],
                                     params)
    
    def cmd_getTimerPeriod(self,params):
        '''emulates
           PORT_TIMER_WIDTH radio_getTimerPeriod()'''
        
        # log the activity
        self.log.debug('cmd_getTimerPeriod')
        
        # defer to radiotimer
        params = self.motehandler.bspRadiotimer.cmd_getPeriod(params,True)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_getTimerPeriod'],
                                     params)
    
    def cmd_setFrequency(self,params):
        '''emulates
           void radio_setFrequency(uint8_t frequency)'''
        
        # unpack the parameters
        (self.frequency,)            = struct.unpack('B', params)
        
        # log the activity
        self.log.debug('cmd_setFrequency frequency='+str(self.frequency))
        
        # change state
        self._changeState(RadioState.SETTING_FREQUENCY)
        
        # change state
        self._changeState(RadioState.FREQUENCY_SET)
        
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
        self._changeState(RadioState.TURNING_OFF)
        
        # update local variable
        self.isRfOn = False
        
        # change state
        self._changeState(RadioState.RFOFF)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rfOff'])
    
    def cmd_loadPacket(self,params):
        '''emulates
           void radio_loadPacket(uint8_t* packet, uint8_t len)'''
        
        # make sure length of params is expected
        assert(len(params)==127+1)
        
        # log the activity
        self.log.debug('cmd_loadPacket len={0}'.format(len(params)))
        
        # change state
        self._changeState(RadioState.LOADING_PACKET)
        
        # update local variable
        length = ord(params[0])
        print length
        
        self.txBuf = []
        self.txBuf.append(length)
        for i in range(1,length+1):
            self.txBuf.append(ord(params[i]))
        output = ''
        for c in self.txBuf:
            output += ' %.2x'%c
        print output
        
        # log
        self.log.debug('txBuf={0}'.format(self.txBuf))
        
        # change state
        self._changeState(RadioState.PACKET_LOADED)
        
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
        self._changeState(RadioState.ENABLING_TX)
        
        # change state
        self._changeState(RadioState.TX_ENABLED)
        
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
        self._changeState(RadioState.ENABLING_RX)
        
        # change state
        self._changeState(RadioState.LISTENING)
        
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
        self._changeState(RadioState.LISTENING)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rxNow'])
    
    def cmd_getReceivedFrame(self,params):
        '''emulates
           void radio_getReceivedFrame(uint8_t* pBufRead,
                                       uint8_t* pLenRead,
                                       uint8_t  maxBufLen,
                                        int8_t* pRssi,
                                       uint8_t* pLqi,
                                       uint8_t* pCrc)'''
        
        # make sure length of params is expected
        assert(len(params)==0)
        
        # log the activity
        self.log.debug('cmd_getReceivedFrame')
        
        #==== prepare response
        # uint8_t rxBuffer[128];
        params  = self.rxBuf[1:]
        while len(params)<128:
            params.append(0)
        # uint8_t len;
        params.append(len(self.rxBuf)-1)
        # int8_t rssi;
        for i in struct.pack('<b',self.rssi):
            params.append(ord(i))
        # uint8_t lqi;
        for i in struct.pack('<b',self.lqi):
            params.append(ord(i))
        # uint8_t crc;
        if self.crcPasses:
            params.append(1)
        else:
            params.append(0)
        assert(len(params)==128+1+1+1+1)
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_getReceivedFrame'],
                                     params)
    
    #======================== interrupts ======================================
    
    def intr_startOfFrame_fromMote(self):
        
        # indicate transmission starts to propagation model
        self.propagation.txStart(self.motehandler.getId(),
                                 self.txBuf,
                                 self.frequency)
        
        # schedule the "end of frame" event
        currentTime          = self.timeline.getCurrentTime()
        endOfFrameTime       = currentTime+self._packetLengthToDuration(len(self.txBuf))
        self.timeline.scheduleEvent(endOfFrameTime,
                                    self.motehandler.getId(),
                                    self.intr_endOfFrame_fromMote,
                                    self.INTR_ENDOFFRAME_MOTE)
        
        # signal start of frame to mote
        counterVal           = self.radiotimer.getCounterVal()
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_isr_startFrame'],
                                     [(counterVal>>0)%0xff,(counterVal>>8)%0xff])
    
    def intr_startOfFrame_fromPropagation(self):
        
        # signal start of frame to mote
        counterVal           = self.radiotimer.getCounterVal()
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_isr_startFrame'],
                                     [(counterVal>>0)%0xff,(counterVal>>8)%0xff])
    
    def intr_endOfFrame_fromMote(self):
        # indicate transmission end to propagation model
        self.propagation.txEnd(self.motehandler.getId())
        
        # signal end of frame to mote
        counterVal           = self.radiotimer.getCounterVal()
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_isr_endFrame'],
                                     [(counterVal>>0)%0xff,(counterVal>>8)%0xff])
    
    def intr_endOfFrame_fromPropagation(self):
        
        # signal end of frame to mote
        counterVal           = self.radiotimer.getCounterVal()
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_isr_endFrame'],
                                     [(counterVal>>0)%0xff,(counterVal>>8)%0xff])
    
    #======================== indication from propagation =====================
    
    def indicateTxStart(self,moteId,packet,channel):
    
        self.log.debug('indicateTxStart from moteId={0} channel={1} len={2}'.format(
            moteId,channel,len(packet)))
    
        if (self.isInitialized==True         and
            self.state==RadioState.LISTENING and
            self.frequency==channel):
            self._changeState(RadioState.RECEIVING)
            self.rxBuf       = packet
            self.rssi        = -50
            self.lqi         = 100
            self.crcPasses   = True
            
            # log
            self.log.debug('rxBuf={0}'.format(self.rxBuf))
            
            # schedule start of frame
            self.timeline.scheduleEvent(self.timeline.getCurrentTime(),
                                        self.motehandler.getId(),
                                        self.intr_startOfFrame_fromPropagation,
                                        self.INTR_STARTOFFRAME_PROPAGATION)
    
    def indicateTxEnd(self,moteId):
        
        self.log.debug('indicateTxEnd from moteId={0}'.format(moteId))
        
        if (self.isInitialized==True and
            self.state==RadioState.RECEIVING):
            self._changeState(RadioState.TXRX_DONE)
            
            # schedule end of frame
            self.timeline.scheduleEvent(self.timeline.getCurrentTime(),
                                        self.motehandler.getId(),
                                        self.intr_endOfFrame_fromPropagation,
                                        self.INTR_ENDOFFRAME_PROPAGATION)
    
    #======================== private =========================================
    
    def _packetLengthToDuration(self,numBytes):
        return float(numBytes*8)/250000.0
        
    def _changeState(self,newState):
        self.state = newState
        self.log.debug('state={0}'.format(self.state))