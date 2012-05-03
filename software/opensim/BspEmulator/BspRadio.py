#!/usr/bin/python

import BspModule

class BspRadio(BspModule.BspModule):
    '''
    \brief Emulates the 'radio' BSP module
    '''
    
    def __init__(self,motehandler):
        
        # store params
        self.motehandler = motehandler
        
        # local variables
        
        # initialize the parent
        BspModule.BspModule.__init__(self,'BspRadio')
    
    #======================== public ==========================================
    
    #=== commands
    
    def cmd_init(self,params):
        '''emulates
           void radio_init()'''
        
        # log the activity
        self.log.debug('cmd_init')
        
        # remember that module has been intialized
        self.isInitialized = True
        
        # respond
        self.motehandler.sendCommand(self.motehandler.commandIds['OPENSIM_CMD_radio_init'])
    
    def cmd_reset(self,params):
        '''emulates
           void radio_reset()'''
        
        # log the activity
        self.log.debug('cmd_reset')
        
        raise NotImplementedError()
    
    def cmd_startTimer(self,params):
        '''emulates
           void radio_startTimer(PORT_TIMER_WIDTH period)'''
        
        # log the activity
        self.log.debug('cmd_startTimer')
        
        raise NotImplementedError()
    
    def cmd_getTimerValue(self,params):
        '''emulates
           PORT_TIMER_WIDTH radio_getTimerValue()'''
        
        # log the activity
        self.log.debug('cmd_getTimerValue')
        
        raise NotImplementedError()
    
    def cmd_setTimerPeriod(self,params):
        '''emulates
           void radio_setTimerPeriod(PORT_TIMER_WIDTH period)'''
        
        # log the activity
        self.log.debug('cmd_setTimerPeriod')
        
        raise NotImplementedError()
    
    def cmd_getTimerPeriod(self,params):
        '''emulates
           PORT_TIMER_WIDTH radio_getTimerPeriod()'''
        
        # log the activity
        self.log.debug('cmd_getTimerPeriod')
        
        raise NotImplementedError()
    
    def cmd_setFrequency(self,params):
        '''emulates
           void radio_setFrequency(uint8_t frequency)'''
        
        # log the activity
        self.log.debug('cmd_setFrequency')
        
        raise NotImplementedError()
    
    def cmd_rfOn(self,params):
        '''emulates
           void radio_rfOn()'''
        
        # log the activity
        self.log.debug('cmd_rfOn')
        
        raise NotImplementedError()
    
    def cmd_rfOff(self,params):
        '''emulates
           void radio_rfOff()'''
        
        # log the activity
        self.log.debug('cmd_rfOff')
        
        raise NotImplementedError()
    
    def cmd_loadPacket(self,params):
        '''emulates
           void radio_loadPacket(uint8_t* packet, uint8_t len)'''
        
        # log the activity
        self.log.debug('cmd_loadPacket')
        
        raise NotImplementedError()
    
    def cmd_txEnable(self,params):
        '''emulates
           void radio_txEnable()'''
        
        # log the activity
        self.log.debug('cmd_txEnable')
        
        raise NotImplementedError()
    
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
        
        raise NotImplementedError()
    
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