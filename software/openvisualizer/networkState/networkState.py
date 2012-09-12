import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('networkState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

from pydispatch import dispatcher

from moteConnector import MoteConnectorConsumer
import RPL

class networkState(MoteConnectorConsumer.MoteConnectorConsumer):
    
    MOP_DIO_A      = 1<<5
    MOP_DIO_B      = 1<<4
    MOP_DIO_C      = 1<<3
    PRF_DIO_A      = 1<<2
    PRF_DIO_B      = 1<<1
    PRF_DIO_C      = 1<<0
    G_DIO          = 1<<7
    
    DIO_PERIOD     = 10 # period between successive DIOs, in seconds
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # initialize parent class
        MoteConnectorConsumer.MoteConnectorConsumer.__init__(
            self,
            signal           = 'inputFromMoteProbe.data.local',
            sender           = dispatcher.Any,
            notifCallback    = self._receivedData_notif
        )
        
        # local variables
        self.stateLock            = threading.Lock()
        self.state                = {}
        self.rpl                  = RPL.RPL()
        
        self.prefix               = None
        self.address              = None
        self.moduleInit           = False
        
        #debug
        self.prefix="2001:1111:2222:3333"
        
        if not self.moduleInit:
            # connect to dispatcher
            dispatcher.connect(
                self._setLocalAddr,
                signal = 'infoDagRoot',
            )
            dispatcher.connect(
                self._setNetworkPrefix,
                signal = 'networkPrefix',
            )
            
            
            #start the moteConnectorConsumer
            self.start()
            
            # send a DIO periodically
            #TODO XV .. enable DIO once tested.
            self._initDIOActivity(self.DIO_PERIOD) 
            self.moduleInit       = True
        
    #======================== public ==========================================
    
    def _receivedData_notif(self,notif):
        
        # log
        log.debug("received {0}".format(notif))
               
        # indicate data to RPL
        self.rpl.update(notif)
    
    #======================== private =========================================
    
    def _initDIOActivity(self,initialPeriod):
        '''
        \brief Start sending DIOs.
        
        \note Only start when the prefix and the current mac address are
              received.
        '''
        self.timer = threading.Timer(initialPeriod,self._sendDIO)
        self.timer.start()
    
    def _sendDIO(self):
        
        if (not self.address) or (not self.prefix):
            self._initDIOActivity(self.DIO_PERIOD)
            return #send only if the prefix is set
        
        li         = []
        
        self.stateLock.acquire() 
        dodagid    = self.prefix   # 16-byte address
        self.stateLock.release() 
        
        dodagid    = dodagid.replace(":","") #remove : from the string
        
        val = self._hextranslate(dodagid) # every 2 digits is an hex that is converted to int.

        for a in val: #build the address, this is the prefix
            li.append(a) 
        
        self.stateLock.acquire()
        for b in self.address: #rest of the address
            li.append(int(b)) 
        self.stateLock.release()
        
        # the list of bytes to be sent to the DAGroot.
        # - [8B]       destination MAC address
        # - [variable] IPHC+ header
        dio = []
        
        #destination one hop address : multicast address set to 0xffffffff
        for i in range(8):
            dio.append(0xff)
        
        # IPHC header
        dio.append(0x78)     # dispatch byte
        dio.append(0x33)     # dam sam
        dio.append(0x3A)     # next header (0x3A=ICMPv6)
        
        # ICMPv6 header
        dio.append(0x00)     # fake byte because of parsing in the iphc module 
                             ## \bug fix this
        dio.append(155)      # ICMPv6 type (155=RPL)
        dio.append(1)        # ICMPv6 CODE (for RPL 0x01=DIO)
        dio.append(0)        # cheksum (byte 1/2), to  be filled later
        dio.append(0)        # cheksum (byte 2/2), to  be filled later
        
        # RPL
        dio.append(0)        # instance ID
        dio.append(0)        # version number
        dio.append(0)        # rank (byte 1/2)
        dio.append(0)        # rank (byte 2/2)
        
        # DIO options
        aux = self.MOP_DIO_A | self.MOP_DIO_B | self.MOP_DIO_C;
        #aux = aux & (not self.PRF_DIO_A) & (not self.PRF_DIO_B) & (not self.PRF_DIO_C) & (not self.G_DIO)
        dio.append(aux)
          
        dio.append(0x33)     # DTSN
        dio.append(0)        # flags
        dio.append(0)        # reserved
        
        # DODAGID
        dio += li
        
        dio.append(0x03)     # options
        
        # checksum of all the fields checksum on ICMP Header
        checksum   = self._calculateCRC(dio[17:], len(dio[17:]))
        dio[15]    = checksum[0]
        dio[16]    = checksum[1]
        
        # log
        log.debug('sending DIO {0}'.format(' '.join(['%.2x'%c for c in dio])))
        
        # dispatch
        dispatcher.send(
            signal        = 'dataForDagRoot',
            sender        = 'rpl',
            data          = ''.join([chr(c) for c in dio]),
        )
        
        # restart the timer
        self._initDIOActivity(self.DIO_PERIOD)
    
    #==== bus event handlers
        
    def _setLocalAddr(self,data):
        self.stateLock.acquire()
        self.address    = data['eui64']
        self.stateLock.release()
        
    def _setNetworkPrefix(self,data):
        self.stateLock.acquire()
        self.prefix     = data    
        self.stateLock.release()
    
    #======================== helpers =========================================
    
    def _calculateCRC(self,payload,length):
        temp_checksum         = [0]*2
        
        self._oneComplementSum(temp_checksum,payload,len(payload));
        temp_checksum[0]     ^= 0xFF;
        temp_checksum[1]     ^= 0xFF;
        
        # log
        log.debug("checksum calculated {0},{1}".format(temp_checksum[0],temp_checksum[1]))
       
        return temp_checksum
    
    def _oneComplementSum(self,checksum,payload,length):
        sum   = 0xFFFF & (checksum[0]<<8 | checksum[1])
        i     = length
        
        while (i>1):
            sum        += 0xFFFF & (payload[length-i]<<8 | (payload[length-i+1]))
            i          -= 2
            
        if (i):
            sum        += (0xFF & payload[length])<<8
   
        while (sum>>16):
            sum         = (sum & 0xFFFF)+(sum >> 16)
   
        checksum[0]     = (sum>>8) & 0xFF
        checksum[1]     = sum & 0xFF
    
    def _hextranslate(self,s):
        assert len(s)%2 == 0
        res = []
        for i in range(len(s)/2):
            realIdx = i*2
            res.append(int(s[realIdx:realIdx+2],16))
        return res
        