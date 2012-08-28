import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('networkState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import RPL
from EventBus import EventBus
from EventBus import Callback

from moteConnector import MoteConnectorConsumer
import binascii

class networkState(MoteConnectorConsumer.MoteConnectorConsumer):
    
    
    MOP_DIO_A = 1 <<5
    MOP_DIO_B = 1 <<4
    MOP_DIO_C = 1 <<3
    PRF_DIO_A = 1 <<2
    PRF_DIO_B = 1 <<1
    PRF_DIO_C = 1 <<0
    G_DIO     = 1 <<7
    
    def __init__(self,moteConnector):
        
        # log
        log.debug("create instance")
        
        # store params
        self.moteConnector                  = moteConnector
        
        # initialize parent class
        MoteConnectorConsumer.MoteConnectorConsumer.__init__(self,self.moteConnector,
                                                                  [self.moteConnector.TYPE_DATA_LOCAL],
                                                                  self._receivedData_notif)
        
        # local variables
        self.stateLock                      = threading.Lock()
        self.state                          = {}
        self.rpl                            = RPL.RPL()
        self.bus                            = EventBus.EventBus()
        
        self.prefix= None
        self.address= None
        
        
        callback = Callback.Callback(self.print_prefix,"networkState.test")
        self.bus.add_listener(callback)
        
        callback = Callback.Callback(self.setLocalAddr,"networkState.setLocalAddr")
        self.bus.add_listener(callback)
        
        callback = Callback.Callback(self.setNetworkPrefix,"networkState.setNetworkPrefix")
        self.bus.add_listener(callback)
        #send a DIO everu 10 seconds.
        #self.initDIOActivity(10) #10s disable DIO activity by now. TODO!! enable it later.
        
    #======================== public ==========================================
    #whenever the prefix and the current mac address are received this function starts the DIO activity.
    def initDIOActivity(self,initialPeriod):
        
        self.timer = threading.Timer(initialPeriod,self._sendDIO)
        self.timer.start()
    
    def print_prefix(self,prefix):
        print "**********************************************"
        print prefix
        
    def setLocalAddr(self,localAddr):
        self.stateLock.acquire()
        self.address=localAddr    
        self.stateLock.release()
        
    def setNetworkPrefix(self,prefix):
        self.stateLock.acquire()
        self.prefix=prefix    
        self.stateLock.release() 
    #======================== private =========================================
    
    def _receivedData_notif(self,notif):
        
        # lg
        log.debug("received {0}".format(notif))
        
        # indicate data to RPL
        self.rpl.update(notif)
        
        
    def _sendDIO(self):
        
        if self.address is None or self.prefix is None:
            self.initDIOActivity(10) #10s
            return #send only if the prefix is set.
        
        li=[] 
        dodagid=self.prefix #16bytes address
        dodagid=dodagid.replace(":","") #remove : from the string
        
        val=self._hextranslate(dodagid)#every 2 digits is an hex that is converted to int.

        for a in val: #build the address, this is the prefix
            li.append(a) 
        
        for b in self.address:#rest of the address
            li.append(int(b)) 
        
        dio =[] #list of bytes
        dio.append(120) #IPHC 0x78
        dio.append(34)  #IPHC 0x22 (dam sam)
        dio.append(58)  #next header icmpv6 (0x3A)
        ## now ICMPv6 header
        
        dio.append(155) #RPL ICMPv6 type 
        dio.append(1) #RPL ICMPv6 CODE 0x01 for DIO
        dio.append(0) #cheksum byte 1  -- little endian??
        dio.append(0) #cheksum byte 2
        
        #RPL specific
        dio.append(0) #RPL instance ID
        dio.append(0) #RPL version number
        dio.append(0) #RPL rank byte 1
        dio.append(0) #RPL rank byte 2
        
        aux = self.MOP_DIO_A | self.MOP_DIO_B | self.MOP_DIO_C;
        aux = aux & (not self.PRF_DIO_A) & (not self.PRF_DIO_B) & (not self.PRF_DIO_C) & (not self.G_DIO)
        
        dio.append(aux) #dio options
          
        dio.append(51) #DTSN 0x33 -- why??
        dio.append(0) #flags
        dio.append(0) #reserved
        
        for k in li: #write the address 128bits to the DIO
            dio.append(k)
        
        dio.append(5) #options 0x05      
        
        dio2send="".join(str(c) for c in dio) #convert list to string
        self.moteConnector.write(dio2send) #send it!
        
        #restart the timer
        self.initDIOActivity(10) #10s
        return
    
    def _hextranslate(self,s):
        assert len(s)%2 == 0
        
        res = []
        for i in range(len(s)/2):
                realIdx = i*2
                res.append(int(s[realIdx:realIdx+2],16))
        return res
        