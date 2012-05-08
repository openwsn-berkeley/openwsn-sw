#!/usr/bin/python

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
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        self.state       = RadioState.STOPPED
        self.frequency   = None
        self.isRfOn      = False
        self.txEnabled   = False
        self.rxEnabled   = False
        self.txBuf       = []
        self.rxBuf       = []
        
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
        
        # update local variable
        self.isRfOff = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rfOff'])
    
    def cmd_loadPacket(self,params):
        '''emulates
           void radio_loadPacket(uint8_t* packet, uint8_t len)'''
        
        # log the activity
        self.log.debug('cmd_loadPacket')
        
        # update local variable
        self.txBuf = []
        for c in params:
            self.txBuf.append(ord(c))
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_loadPacket'])
    
    def cmd_txEnable(self,params):
        '''emulates
           void radio_txEnable()'''
        
        # log the activity
        self.log.debug('cmd_txEnable')
        
        # make sure that radio is on
        assert(self.isRfOn)
        
        # update local variable
        self.txEnabled = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_txEnable'])
    
    def cmd_txNow(self,params):
        '''emulates
           void radio_txNow()'''
        
        # log the activity
        self.log.debug('cmd_txNow')
        
        raise NotImplementedError()
    
    def cmd_rxEnable(self,params):
        '''emulates
           void radio_rxEnable()'''
        
        # log the activity
        self.log.debug('cmd_rxEnable')
        
        # make sure that radio is on
        assert(self.isRfOn)
        
        # update local variable
        self.rxEnabled = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_rxEnable'])
    
    def cmd_rxNow(self,params):
        '''emulates
           void radio_rxNow()'''
        
        # log the activity
        self.log.debug('cmd_rxNow')
        
        raise NotImplementedError()
    
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
    
    #======================== private =========================================