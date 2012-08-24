import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('networkState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import RPL

from moteConnector import MoteConnectorConsumer

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
        
    
        #send a DIO everu 10 seconds.
        
    #======================== public ==========================================
    #whenever the prefix and the current mac address are received this function starts the DIO activity.
    def initDIOActivity(self,prefix,address,initialPeriod):
        
        self.prefix=prefix 
        self.address=address  #local address
        self.timer = Timer(initialPeriod,self._sendDIO)
        self.timer.start()
    
    #======================== private =========================================
    
    def _receivedData_notif(self,notif):
        
        # lg
        log.debug("received {0}".format(notif))
        
        # indicate data to RPL
        self.rpl.update(notif)
        
        
    def _sendDIO(self):
        
        
        dodagid=self.prefix #16bytes address
        dodagid.append(self.address)

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
        
        aux = MOP_DIO_A | MOP_DIO_B | MOP_DIO_C;
        aux = aux & (not PRF_DIO_A) & (not PRF_DIO_B) & (not PRF_DIO_C) & (not G_DIO)
        
        dio.append(aux) #dio options
          
        dio.append(51) #DTSN 0x33 -- why??
        dio.append(0) #flags
        dio.append(0) #reserved
        dio.append(dodagid)
        dio.append(5) #options 0x05      
        
        self.moteConnector.write(dio)
        
        return
    
        