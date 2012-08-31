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
    
    DIO_PERIOD = 20 #20s period
    
    #An indetified problem comes when more than mote is attached to the serial port. The moteStateGui instantiate a networkState 
    #for each mote connected to the computer. hence a network state is also created for motes that are not the Dagroot. 
    #in that situation the problem is that networkState starts another DIO timer which increases the frequency of DIOs being sent.
    #This BUG need to be fixed by preventing more instances of networkState. An option is to make it a singleton, another option
    #is to identify the serial port of the dagroot and only create a network state that writes to that serial port. 
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
        
        self.prefix                         = None
        self.address                        = None
        self.moduleInit                     = False
        
        if self.moduleInit==False:
            callback = Callback.Callback(self.print_prefix,"networkState.test")
            self.bus.add_listener(callback)
            
            callback = Callback.Callback(self.setLocalAddr,"networkState.setLocalAddr")
            self.bus.add_listener(callback)
            
            callback = Callback.Callback(self.setNetworkPrefix,"networkState.setNetworkPrefix")
            self.bus.add_listener(callback)
            #send a DIO everu 10 seconds.
            #TODO XV .. enable DIO once tested.
            self.initDIOActivity(self.DIO_PERIOD) 
            self.moduleInit                     = True
        
    #======================== public ==========================================
    #whenever the prefix and the current mac address are received this function starts the DIO activity.
    def initDIOActivity(self,initialPeriod):
        
        self.timer = threading.Timer(initialPeriod,self._sendDIO)
        self.timer.start()
    
    def print_prefix(self,prefix):
        #print "**********************************************"
        print "[PREFIX] "+prefix
        
    def setLocalAddr(self,localAddr):
        self.stateLock.acquire()
        self.address=localAddr    
        self.stateLock.release()
        
    def setNetworkPrefix(self,prefix):
        self.stateLock.acquire()
        self.prefix=prefix    
        self.stateLock.release() 
    #======================== private =========================================
   
   
    def _calculateCRC(self,payload,length):
       
       temp_checksum = [0]*2
       little_helper = []
       
       #initialization
       #temp_checksum[0]  = 0;
       #temp_checksum[1]  = 0;
      
      
       self._oneComplementSum(temp_checksum,payload,len(payload));
       temp_checksum[0] ^= 0xFF;
       temp_checksum[1] ^= 0xFF;
       log.debug("checksum calculated {0},{1}".format(temp_checksum[0],temp_checksum[1]))
       return temp_checksum
    
    def _oneComplementSum(self,checksum,payload,length):
        sum = 0xFFFF & (checksum[0]<<8 | checksum[1])
        i=length
        while (i>1):
            sum     += 0xFFFF & (payload[length-i]<<8 | (payload[length-i+1]))
            i  -= 2
            
        if (i):
            sum     += (0xFF & payload[length])<<8
   
        while (sum>>16) :
            sum      = (sum & 0xFFFF)+(sum >> 16);
   
        checksum[0] = (sum>>8) & 0xFF;
        checksum[1] = sum & 0xFF;
        
    
    def _receivedData_notif(self,notif):
        
        # lg
        log.debug("received {0}".format(notif))
        
        # indicate data to RPL
        self.rpl.update(notif)
        
        
    def _sendDIO(self):
        
        if self.address is None or self.prefix is None:
            self.initDIOActivity(self.DIO_PERIOD) #10s
            return #send only if the prefix is set.
        
        li=[]
        
        self.stateLock.acquire() 
        dodagid=self.prefix #16bytes address
        self.stateLock.release() 
        
        dodagid=dodagid.replace(":","") #remove : from the string
        
        val=self._hextranslate(dodagid)#every 2 digits is an hex that is converted to int.

        for a in val: #build the address, this is the prefix
            li.append(a) 
        
        self.stateLock.acquire()
        for b in self.address:#rest of the address
            li.append(int(b)) 
        self.stateLock.release()
        
        dio =[] #list of bytes
        #destination one hop address : multicast address set to 0xffffffff
        for i in range(8):
            dio.append(255) #0xff
            
        dio.append(120) #IPHC 0x78
        dio.append(0x33)  #IPHC 0x33 (dam sam)
        dio.append(58)  #next header icmpv6 (0x3A)
        ## now ICMPv6 header
        dio.append(9) #fake byte because the parsing in the iphc module in the mote requires that. Check why!!! any number works.
        
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
        
        #calculate checksum of all the fields after checksum on ICMP Header
        checksum=self._calculateCRC(dio[17:], len(dio[17:]))
        dio[15]=checksum[0]
        dio[16]=checksum[1]
        
        dio2send="".join(chr(c) for c in dio) #convert list to string
        #dio2print="".join(str(c) for c in dio) #convert list to string
        dio2hex="".join(hex(c) for c in dio) #convert list to string
        print dio2hex
        
        self.moteConnector.write(dio2send) #send it!
        
        #restart the timer
        self.initDIOActivity(self.DIO_PERIOD) #10s
        return
    
    def _hextranslate(self,s):
        assert len(s)%2 == 0
        
        res = []
        for i in range(len(s)/2):
                realIdx = i*2
                res.append(int(s[realIdx:realIdx+2],16))
        return res
        