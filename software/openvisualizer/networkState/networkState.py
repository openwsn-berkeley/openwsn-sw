import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('networkState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import struct
from pprint import pprint
from datetime import datetime

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
        
        self.latencyStats     = {} #empty dictionary
        
        #debug when lbr does not work
        #self.prefix="2001:1111:2222:3333"
        
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
            #subscribe to LBR data to handle source routing.
            dispatcher.connect(
                self._IPv6PacketReceived,
                signal = 'dataFromInternet',
            )
            #get latency information 
            dispatcher.connect(
                self._latencyStatsRcv,
                signal = 'latency',
            )
            
            #start the moteConnectorConsumer
            self.start()
            
            # send a DIO periodically
            self._initDIOActivity(self.DIO_PERIOD) 
            self.moduleInit       = True
        
    #======================== public ==========================================
    ''' This method is invoked whenever a UDP packet is send from a mote from UDPLatency application. This app listens at port 61001 
        and computes the latency of a packet. Note that this app is a crosslayer app since the mote sends the data within a UDP packet 
        and OpenVisualizer (ParserData) handles that packet and reads UDP payload to compute time difference. At bridge level on the dagroot, 
        the ASN of the DAGROOt is appended to the serial port to be able to know what is the ASN at reception side. The LATENCY values are in uS.'''  
    def _latencyStatsRcv(self,data):
        address=",".join(hex(c) for c in data[0])
        latency=data[1]
        parent=",".join(hex(c) for c in data[2])
        
        stats={}#dictionary of stats
        
        if (self.latencyStats.get(str(address)) is None):
           #none for this node.. create initial stats
           stats.update({'min':latency})
           stats.update({'max':latency})
           stats.update({'num':1})
           stats.update({'avg':latency})
           stats.update({'parentSwitch':1})#changes of parent
        else:
            #get and update
           stats=self.latencyStats.get(str(address))
           if (stats.get('min')>latency):
               stats.update({'min':latency})
           if (stats.get('max')<latency):
               stats.update({'max':latency})
           stats.update({'avg':((stats.get('avg')*stats.get('num'))+latency)/(stats.get('num')+1)})
           stats.update({'num':(stats.get('num')+1)})
           if (stats.get('prefParent')!=parent):
               stats.update({'parentSwitch':(stats.get('parentSwitch')+1)})#record parent change since last message
        #this fields are common
        stats.update({'lastVal':latency})
        stats.update({'prefParent':parent})
        stats.update({'lastMsg':datetime.now()})
        
        self.stateLock.acquire()  
        self.latencyStats.update({str(address):stats}) 
        self.stateLock.release()               
        #add to dictionary and compute stats...
        log.debug("Latency stats in mS {0}".format(self.latencyStats))
        pprint(self.latencyStats)        
        
    
      # the data received from the LBR should be:
      # - first 8 bytes: EUI64 of the final destination
      # - remainder: 6LoWPAN packet and above
    def _IPv6PacketReceived(self,data):
        #destination needs to be unpacked
        dest =struct.unpack('<BBBBBBBB',''.join([c for c in data[:8]])) 
        #test only
        #dest=data[:8]
        destination = list(dest)
       
        log.debug("packet to be sent to {0}".format("".join(str(c) for c in destination)))
        
        if (self._isbroadcast(destination)):
            #bypass source routing as it is a broadcast packet.
            #this is a RADV, once RPL works perfectly this pkt should be destroyed instead.
            lowpanmsg=data
            
            log.debug("broadcast packet {0}".format("".join(str(c) for c in data)))
            #return #nothing is send RADV are not needed.
        else:    
            #pkt to a specific address
            pkt=data[8:] 
            # a source route in the routing table looks like that:
            #{'[20, 21, 146, 11, 3, 1, 0, 233]': [[20, 21, 146, 11, 3, 1, 0, 233]]}
            route=self.rpl.getRouteTo(destination)
            if not route:
                #can be me!!
                log.debug("No route to required destination {0}".format("".join(str(c) for c in destination)))
                #is that possible that this packet is an icmpv6 router adv? a ping??
                #We decided that the GW is only L2 and hence cannot be ping etc...
                return #the list is empty. no route to host. TODO Check if this is the desired behaviour.
            
            # the route is here.
            log.debug("route src found {0}".format(route))
            route.pop() #remove the last element as it is this node!!
            
            if (len(route)>1):
                #more than one hop -- create the source routing header. 
                srcRouteHeader=[]
                srcRouteHeader.append(0x2b) #Next header should be 43 as RFC2460 page 11.
                 
                srcRouteHeader.append(0) #len of the routing header. to be set later
                srcRouteHeader.append(0x03) #Routing type 3 fir src routing
                srcRouteHeader.append(len(route)-1) #number of hops -- segments left . -1 because the first hop goes to the ipv6 destination address.
                elided=0x08<<4 & 0x08 
                srcRouteHeader.append(elided) #elided prefix -- all in our case
                srcRouteHeader.append(0) #padding octets
                srcRouteHeader.append(0) #reserved
                srcRouteHeader.append(0) #reserved
                nextHop=list(route[0]) #this is the next hop that goes in front of the pkt so openserial can read it
                for j in range(1,len(route)):
                    hop=route[j]
                    for i in range(len(hop)):
                         srcRouteHeader.append(hop[i]) #reserved
                
                #now set the length 
                srcRouteHeader[1]=len(srcRouteHeader)
                #10 bytes ipv6 header
                ipv6header=pkt[:10]
                pkt=pkt[10:]
                #Split the packet, add the src routing header
                #build the pkt as NEXT HOP + IPv6 Header + SRC ROUTING HEADER + REST OF THE PKT
                for c in ipv6header:  
                    nextHop.append(c)
                for c in srcRouteHeader:
                    nextHop.append(c)
                for d in pkt:
                    nextHop.append(d)
                    
                #TODO No fragmentation so we need to check the size!!!!
                if len(nextHop)>136:#127+8
                     log.debug("packet too long. size {0}".format(len(nextHop)))
                     return    
                # pkt reasembled with the src routing header. SEND IT
                lowpanmsg="".join(c for c in nextHop)
                
                #debug xv
                #lowpanmsg="".join(str(c) for c in nextHop)
                
            else:
                log.debug("destination is next hop")
                #--> destination is next hop.
                # let the packet as is??
                if len(data)>136:#127+8
                     log.debug("packet too long. size {0}".format(len(data)))
                     print "packet too long. size {0}".format(len(data))
                     return    
                
                lowpanmsg=data
                pass     
            
        dispatcher.send(
            signal        = 'dataForDagRoot',
            sender        = 'rpl',
            data          = lowpanmsg,
        )
               
        return
    
    
    def _isbroadcast(self,destination):
        a = True
        for x in destination:
            a=(a and (x==255))
        return a;
        
        
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
        dio[14]    = checksum[0]
        dio[15]    = checksum[1]
        
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
        