'''
\brief Module which coordinate RPL DIO and DAO messages.

\author Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>, January 2013.
'''

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
    
    LINK_LOCAL_PREFIX        = "FE80:0000:0000:0000"       ##< IPv6 link-local prefix.
    MAX_SERIAL_PKT_SIZE      = 8+127                       ##< Maximum length for a serial packet.
    DIO_PERIOD               = 10                          ##< period between successive DIOs, in seconds.
    
    # http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml 
    IANA_UNDEFINED           = 0x00
    IANA_PROTOCOL_UDP        = 17
    IANA_PROTOCOL_IPv6ROUTE  = 43
    
    #=== 6LoWPAN header (RFC6282)
    # byte 0
    SR_DISPATCH_MASK         = 3<<5                        ##< Dispatch
    SR_TF_MASK               = 3<<3                        ##< Traffic Fields
    SR_NH_SET                = 0x01                        ##< Next Header
    SR_NH_MASK               = SR_NH_SET<<2                ##< not compressed next header as we need to advertise src routing header
    SR_HLIM_MASK             = 1<<0                        ##< Hop Limit
    # byte 1
    SR_CID_MASK              = 0                           ##< Context Identifier Extension
    SR_SAC_MASK              = 0                           ##< Source Address Compression
    SR_SAM_MASK              = 0                           ##< Source Address Mode
    SR_M_MASK                = 0                           ##< Multicast Compression
    SR_DAC_MASK              = 0                           ##< Destination Address Compression
    SR_DAM_MASK              = 3                           ##< Destination Address Mode
    # inline next header
    SR_NH_VALUE              = IANA_PROTOCOL_IPv6ROUTE     ##< Next header
    
    #=== RPL source routing header (RFC6554)
    SR_FIR_TYPE              = 0x03                        ##< Routing Type
    
    #=== UDP header (RFC768)
    NHC_UDP_MASK             = 0xF8                        ##< b1111 1000
    NHC_UDP_ID               = 0xF0                        ##< b1111 0000
    
    #=== RPL DIO (RFC6550)
    DIO_OPT_GROUNDED         = 1<<7
    MOP_DIO_A                = 1<<5
    MOP_DIO_B                = 1<<4
    MOP_DIO_C                = 1<<3
    PRF_DIO_A                = 1<<2
    PRF_DIO_B                = 1<<1
    PRF_DIO_C                = 1<<0
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # initialize parent class
        MoteConnectorConsumer.MoteConnectorConsumer.__init__(
            self,
            signal           = 'inputFromMoteProbe.data.local',
            sender           = dispatcher.Any,
            notifCallback    = self._receivedMoteDataLocal_notif
        )
        
        # local variables
        self.stateLock       = threading.Lock()
        self.state           = {}
        self.rpl             = RPL.RPL()
        self.networkPrefix   = self.LINK_LOCAL_PREFIX
        self.dagRootEui64    = None
        self.moduleInit      = False
        self.latencyStats    = {}
        
        if not self.moduleInit:
            # connect to dispatcher
            dispatcher.connect(
                self._setDagRootEui64,
                signal       = 'infoDagRoot',
            )
            dispatcher.connect(
                self._setNetworkPrefix,
                signal       = 'networkPrefix',
            )
            # subscribe to LBR data to handle source routing.
            dispatcher.connect(
                self._receivedInternetData_notif,
                signal       = 'dataFromInternet',
            )
            # get latency information 
            dispatcher.connect(
                self._latencyStatsRcv,
                signal       = 'latency',
            )
            
            # start the moteConnectorConsumer
            self.start()
            
            # send a DIO periodically
            self._scheduleSendDIO(self.DIO_PERIOD) 
            self.moduleInit  = True
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #==== handle bus commands
    
    def _setDagRootEui64(self,data):
        '''
        \brief Record the DAGroot's EUI64 address.
        '''
        with self.stateLock:
            self.dagRootEui64     = data['eui64']
    
    def _setNetworkPrefix(self,data):
        '''
        \brief Record the network prefix.
        '''
        with self.stateLock:
            self.networkPrefix    = data
    
    #===== send DIO
    
    def _scheduleSendDIO(self,interval):
        '''
        \brief Schedule to send a DIO sometime in the future.
        
        \param[in] interval In how many seconds the DIO is scheduled to be
            sent.
        '''
        self.timer = threading.Timer(interval,self._sendDIO)
        self.timer.start()
    
    def _sendDIO(self):
        '''
        \brief Send a DIO.
        '''
        # don't send DIO if I didn't discover the DAGroot EUI64.
        if not self.dagRootEui64:
            
            # reschule to try again later
            self._scheduleSendDIO(self.DIO_PERIOD)
            
            # stop here
            return
        
        # the list of bytes to be sent to the DAGroot.
        # - [8B]       destination MAC address
        # - [variable] IPHC+ header
        dio                  = []
        
        # next hop: broadcast address
        dio                 += [0xff]*8
        
        # IPHC header
        dio                 += [0x78]        # dispatch byte
        dio                 += [0x33]        # dam sam
        dio                 += [0x3A]        # next header (0x3A=ICMPv6)
        dio                 += [0x00]        # HLIM
        
        # ICMPv6 header
        idxICMPv6            = len(dio)      # remember where ICMPv6 starts
        dio                 += [155]         # ICMPv6 type (155=RPL)
        dio                 += [0x01]        # ICMPv6 CODE (for RPL 0x01=DIO)
        idxICMPv6CS          = len(dio)      # remember where ICMPv6 checksum starts
        dio                 += [0x00,0x00]   # placeholder for checksum (filled out later)
        
        # DIO header
        dio                 += [0x00]        # instance ID
        dio                 += [0x00]        # version number
        dio                 += [0x00,0x00]   # rank
        dio                 += [
                                  self.DIO_OPT_GROUNDED |
                                  self.MOP_DIO_A        |
                                  self.MOP_DIO_B        |
                                  self.MOP_DIO_C
                               ]             # options: G | 0 | MOP | Prf
        dio                 += [0x00]        # DTSN
        dio                 += [0x00]        # flags
        dio                 += [0x00]        # reserved
        
        # DODAGID
        with self.stateLock:
            dio             += self._hexstring2bytelist(self.networkPrefix.replace(':',''))
            dio             += self.dagRootEui64
        
        # calculate ICMPv6 checksum over ICMPv6header+ (RFC4443)
        checksum             = self._calculateCRC(
                                   dio[idxICMPv6:],
                                   len(dio[idxICMPv6:])
                               )
        dio[idxICMPv6CS  ]   = checksum[0]
        dio[idxICMPv6CS+1]   = checksum[1]
        
        # log
        log.debug('sending DIO {0}'.format(self._formatByteList(dio)))
        
        # dispatch
        dispatcher.send(
            signal        = 'dataForDagRoot',
            sender        = 'rpl',
            data          = ''.join([chr(c) for c in dio]),
        )
        
        # schedule the next DIO transmission
        self._scheduleSendDIO(self.DIO_PERIOD)
    
    #===== received DAO
    
    def _receivedMoteDataLocal_notif(self,notif):
        '''
        \brief Called when receiving inputFromMoteProbe.data.local, probably a DAO.
        '''
        
        # log
        log.debug("received data local {0}".format(self._formatByteList(notif)))
               
        # indicate data to RPL
        self.rpl.indicateDAO(notif)
    
    #===== received dataFromInternet
    
    def _receivedInternetData_notif(self,data):
        
        # packet received from LBR consists of:
        # - [8B]        final destination's EUI64
        # - [variable]  packet, starting with 6LoWPAN header
        destination     = [ord(b) for b in data[:8]]
        packet          = [ord(b) for b in data[8:]]
        
        # log
        output          = []
        output         += ['Received packet from Internet:']
        output         += [' - destination: {0}'.format(self._formatByteList(destination))]
        output         += [' - packet:      {0}'.format(self._formatByteList(packet))]
        output          = '\n'.join(output)
        log.debug(output)
        
        if destination==[0xff]*len(destination):
            # this packet is destined to broadcast address
            
            # log
            log.debug("Packet for broadcast, dropping.")
            
            # stop here: we don't want to send broadcast packets into mesh
            return
            
        # get source route to destination
        route           = self.rpl.getRouteTo(destination)
        if not route:
            log.warning("No known source route to {0}".format(''.join(str(c) for c in destination)))
            return
       
        # if you get here, a source route was found
        
        # log
        log.debug("source route to {0}: {1}".format(destination,route))
        
        # remove last source routing element, which is DAGroot
        route.pop()
        
        if (len(route)>1):
            
            log.debug("Destination is more that one hop away.")
            
            # Insert a source routing header into packet.
            
            #   lowpan [2B]
            #      dispatch:         0x3
            #      tf:               0x3 (elided traffic fields)
            #      nh:               0x1 (next-header compressed)
            #      hlim:             0x1 (1 hop max)
            #      cid:              0x0 (no inline context id)
            #      sac:              0x0 (stateless src. addr. compr.)
            #      sam:              0x0 (128b in-line addr.)
            #      m:                0x0 (unicast)
            #      dac:              0x0 (stateless dest. addr. compr.)
            #      dam:              0x3 (elided addr., or 8b multicast)
            #   src address [16B]
            #      src_addr:         200104701f120f200000000000000002
            #   dest address [0B]
            #      dest_addr:       
            #   udp
            #      c:                0x1 (elided udp checksum)
            #      p:                0x0 (udp port bits: s16_d16)
            #      src_port:         0xa3b5
            #      dest_port:        0x8
            #   payload
            #      length:           0x4
            #      bytes:            6161610a
            
            iphcBytes                  = packet[:2]
            
            # extract nextHeaderVal and expandUDP
            nextHeaderVal              = self.IANA_UNDEFINED
            expandUDP                  = False
            if (((iphcBytes[0]>>2) & self.SR_NH_SET)==1):
                # next header is compressed. check if it is UDP
                srcAddress             = packet[2:2+16]
                maybeUDP               = packet[2+16:2+16+1]
                if ((maybeUDP[0]&self.NHC_UDP_MASK)==self.NHC_UDP_ID):
                    nextHeaderVal      = self.IANA_PROTOCOL_UDP
                    expandUDP          = True
                    packet             = packet[2+16:]
            else:
                # next header is not compressed, read directly from IPHC field
                nextHeaderVal          = packet[2]
                srcAddress             = packet[3:19]
                expandUDP              = False      
                packet                 = packet[2+1+16:]
            
            # log
            log.debug('nextHeaderVal={0} expandUDP={1}'.format(nextHeaderVal,expandUDP))
            
            # modify IPHC header
            iphcBytes[0]               = self.SR_DISPATCH_MASK      | \
                                         self.SR_TF_MASK            | \
                                         ((~self.SR_NH_MASK) & 0x0f)| \
                                         self.SR_HLIM_MASK
            iphcBytes[1]               = self.SR_CID_MASK           | \
                                         self.SR_SAC_MASK           | \
                                         self.SR_SAM_MASK           | \
                                         self.SR_M_MASK             | \
                                         self.SR_DAC_MASK           | \
                                         self.SR_DAM_MASK
            iphcBytes                 += [self.SR_NH_VALUE]
            
            # create the src route header
            srcRouteHeader             = self._createSrcRouteHeader(nextHeaderVal,route)
            
            # expand the UDP header, if needed
            if expandUDP:
                expandedUdpDatagram    = self._expandUDPdatagram(packet)     
            else:
                expandedUdpDatagram    = []
            
            # Assemble bytes to send
            bytesToSend      = []
            bytesToSend     += route[-1]              # next hop's EUI64
            bytesToSend     += iphcBytes              # IPHC bytes
            bytesToSend     += srcAddress             # source address
            bytesToSend     += srcRouteHeader         # source routing header
            if expandUDP:
                bytesToSend += expandedUdpDatagram    # expanded UDP datagram (includes payload)
            else:
                bytesToSend += packet                 # untouched payload
            
        else:
            
            log.debug("Destination is one hop away.")
            
            # Assemble bytes to send
            bytesToSend      = []
            bytesToSend     += destination            # untouched destination
            bytesToSend     += packet                 # untouched packet
        
        # verify max length
        if len(bytesToSend)>self.MAX_SERIAL_PKT_SIZE:
            log.error("packet too long, size={0}".format(len(nextHop)))
            return  
        
        dispatcher.send(
            signal           = 'dataForDagRoot',
            sender           = 'rpl',
            data             = ''.join([chr(b) for b in bytesToSend]),
        )
    
    def _createSrcRouteHeader(self, nextHeaderVal, route):
        '''
        \brief Creates a source routing header.
        
        Header format described in http://tools.ietf.org/html/rfc6554#section-3.
        '''
        
        # create header
        returnVal            = []
        returnVal           += [nextHeaderVal]             # Next Header.
        returnVal           += [len(route)-1]              # Hdr Ext Len. -1 to remove last element.
        returnVal           += [self.SR_FIR_TYPE]          # Routing Type. 3 for source routing.
        returnVal           += [len(route)-1]              # Segments Left. -1 because the first hop goes to the ipv6 destination address.
        returnVal           += [0x08 << 4 | 0x08]          # CmprI | CmprE. All prefixes elided.
        returnVal           += [0x00,0x00,0x00]            # padding (4b) + reserved (20b)
        for j in range(1,len(route)):
            hop              = route[(len(route)-1)-j]     # first hop not needed
            returnVal       += hop
            
        # log
        output               = []
        output               = ['creating source header:']
        output               = ['- nextHeaderVal: {0}'.format(nextHeaderVal)]
        output               = ['- route:         {0}'.format(route)]
        output               = ['- returnVal:     {0}'.format(self._formatByteList(returnVal))]
        output               = '\n'.join(output)
        log.debug(output)
        
        # return header
        return returnVal
    
    def _expandUDPdatagram(self, pkt):
        '''
        \brief Turn a 6LoWPAN-compacted UDP header into a full-blown one.
        
        The formats are defined by:
        - 6LoWPAN-compacted UDP header: http://tools.ietf.org/html/rfc6282#section-4.3.3
        - full-blown UDP header:        http://tools.ietf.org/html/rfc768
        
        \param[in] pkt A bytelist representing a packet, starting after the
            6LoWPAN header, i.e. at the UDP LOWPAN_NHC Format.
        
        \return A bytelist representing the same packet, but with full-blown
            UDP header.
        '''
        oldUdp               = pkt[:5]
        
        # format new UDP header
        newUdp               = []
        newUdp              += oldUdp[1:3]                 # Source Port
        newUdp              += oldUdp[3:5]                 # Destination Port
        length               = 8+len(pkt[5:])
        newUdp              += [(length & 0xFF00) >> 8]    # Length
        newUdp              += [(length & 0x00FF) >> 0]
        idxCS                = len(newUdp)                 # remember index of checksum
        newUdp              += [0x00,0x00]                 # Checksum (placeholder) 
        newUdp              += pkt[5:]                     # data octets
        
        # calculate checksum (do last)
        checksum             = self._calculateCRC(newUdp, len(newUdp))
        newUdp[idxCS]        = checksum[0]
        newUdp[idxCS+1]      = checksum[1]
        
        return newUdp
    
    #===== received latency data
    
    def _latencyStatsRcv(self,data):
        '''
        This method is invoked whenever a UDP packet is send from a mote from
        UDPLatency application. This application listens at port 61001 and 
        computes the latency of a packet. Note that this app is crosslayer
        since the mote sends the data within a UDP packet and OpenVisualizer
        (ParserData) handles that packet and reads UDP payload to compute time
        difference.
        
        At the bridge module on the DAGroot, the ASN of the DAGroot is appended
        to the serial port to be able to know what is the ASN at reception
        side.
        
        Calculcate latency values are in us.
        '''
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
    
    #======================== helpers =========================================
    
    def _formatByteList(self,l):
        '''
        \brief Format a bytelist into an easy-to-read string.
        
        That is:  [0xab,0xcd,0xef,0x00] -> '(4 bytes) ab-cd-ef-00'
        '''
        return '({0} bytes) {1}'.format(len(l),'-'.join(["%02x"%b for b in l]))
    
    def _calculateCRC(self,payload,length):
        temp_checksum         = [0]*2
        
        self._oneComplementSum(temp_checksum,payload,len(payload));
        temp_checksum[0]     ^= 0xFF;
        temp_checksum[1]     ^= 0xFF;
        
        # log
        log.debug("checksum calculated {0:x},{1:x}".format(temp_checksum[0],temp_checksum[1]))
       
        return temp_checksum
    
    def _oneComplementSum(self,checksum,payload,length):
        sum   = 0xFFFF & (checksum[0]<<8 | checksum[1])
        i     = length
        
        while (i>1):
            sum        += 0xFFFF & (payload[length-i]<<8 | (payload[length-i+1]))
            i          -= 2
            
        if (i):
            sum        += (0xFF & payload[length-1])<<8
   
        while (sum>>16):
            sum         = (sum & 0xFFFF)+(sum >> 16)
   
        checksum[0]     = (sum>>8) & 0xFF
        checksum[1]     = sum & 0xFF
    
    def _hexstring2bytelist(self,s):
        '''
        \brief Convert a string of hex caracters into a byte list.
        
        That is: 'abcdef00' -> [0xab,0xcd,0xef,0x00]
        
        \param[in] s The string to convert
        
        \returns A list of integers, each element in [0x00..0xff].
        '''
        assert type(s)==str
        assert len(s)%2 == 0
        
        returnVal = []
        
        for i in range(len(s)/2):
            realIdx = i*2
            returnVal.append(int(s[realIdx:realIdx+2],16))
        
        return returnVal
        