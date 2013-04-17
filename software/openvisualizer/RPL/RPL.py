'''
\brief Module which coordinate RPL DIO and DAO messages.

\author Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>, January 2013.
\author Thomas Watteyne <watteyne@eecs.berkeley.edu>, April 2013.
'''

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('RPL')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import struct
from datetime import datetime

from pydispatch import dispatcher

from eventBus import eventBusClient
import SourceRoute

import openvisualizer_utils as u

class RPL(eventBusClient.eventBusClient):
    
    LINK_LOCAL_PREFIX             = "FE80:0000:0000:0000"       ##< IPv6 link-local prefix.
    
    MAX_SERIAL_PKT_SIZE           = 8+127                       ##< Maximum length for a serial packet.
    DIO_PERIOD                    = 10                          ##< period between successive DIOs, in seconds.
    
    # http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml 
    IANA_UNDEFINED                = 0x00
    IANA_PROTOCOL_UDP             = 17
    IANA_PROTOCOL_IPv6ROUTE       = 43
    IANA_ICMPv6_RPL_TYPE          = 155              
    #=== 6LoWPAN header (RFC6282)
    # byte 0
    SR_DISPATCH_MASK              = 3<<5                        ##< Dispatch
    SR_TF_MASK                    = 3<<3                        ##< Traffic Fields
    SR_NH_SET                     = 0x01                        ##< Next Header
    SR_NH_MASK                    = SR_NH_SET<<2                ##< not compressed next header as we need to advertise src routing header
    SR_HLIM_MASK                  = 1<<0                        ##< Hop Limit
    # byte 1
    SR_CID_MASK                   = 0                           ##< Context Identifier Extension
    SR_SAC_MASK                   = 0                           ##< Source Address Compression
    SR_SAM_MASK                   = 0                           ##< Source Address Mode
    SR_M_MASK                     = 0                           ##< Multicast Compression
    SR_DAC_MASK                   = 0                           ##< Destination Address Compression
    SR_DAM_MASK                   = 3                           ##< Destination Address Mode
    # inline next header
    SR_NH_VALUE                   = IANA_PROTOCOL_IPv6ROUTE     ##< Next header
    
    #=== RPL source routing header (RFC6554)
    SR_FIR_TYPE                   = 0x03                        ##< Routing Type
    
    #=== UDP header (RFC768)
    NHC_UDP_MASK                  = 0xF8                        ##< b1111 1000
    NHC_UDP_ID                    = 0xF0                        ##< b1111 0000
    
    #=== RPL DIO (RFC6550)
    DIO_OPT_GROUNDED              = 1<<7
    MOP_DIO_A                     = 1<<5
    MOP_DIO_B                     = 1<<4
    MOP_DIO_C                     = 1<<3
    PRF_DIO_A                     = 1<<2
    PRF_DIO_B                     = 1<<1
    PRF_DIO_C                     = 1<<0
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        
        # store params
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'RPL',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getSourceRoute',
                    'callback'    : self._getSourceRoute_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'infoDagRoot',
                    'callback'    : self._infoDagRoot_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'networkPrefix',
                    'callback'    : self._networkPrefix_notif,
                },
            ]
        )
        
        # local variables
        self.stateLock            = threading.Lock()
        self.state                = {}
        self.sourceRoute          = SourceRoute.SourceRoute()
        self.networkPrefix        = self.LINK_LOCAL_PREFIX
        self.dagRootEui64         = None
        self.latencyStats         = {}
        
        # send a DIO periodically
        self._scheduleSendDIO(self.DIO_PERIOD) 
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #==== handle EventBus notifications
    
    def _fromMoteDataLocal_notif(self,sender,signal,data):
        '''
        \brief Called when receiving fromMote.data.local, probably a DAO.
        '''
        
        # log
        #log.debug("received data local {0}".format(self._formatByteList(data)))
               
        # indicate data to sourceRoute
        self.sourceRoute.indicateDAO(data)
        return True
    
    def _getSourceRoute_notif(self,sender,signal,data):
        destination = data
        return self.sourceRoute.getSourceRoute(destination)
    
    
    #TODO when we get assigned a prefix and a moteid, then we can subscribe to ICMPv6, DAO Type for our address
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        \brief Record the DAGroot's EUI64 address.
        '''
        with self.stateLock:
            self.dagRootEui64     = []
            for c in data['eui64']:
                self.dagRootEui64     +=[int(c)]
        #signal to which this component is subscribed.
        signal=(",".join(chr(c) for c in (self.networkPrefix + self.dagRootEui64)),self.PROTO_ICMPv6,self.IANA_ICMPv6_RPL_TYPE)
        #register as soon as I get an address
        self.register(self.WILDCARD,signal,self._fromMoteDataLocal_notif)    
         
    def _networkPrefix_notif(self,sender,signal,data):
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
        nextHop              = [0xff]*8
        
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
            dio             += self.networkPrefix #self._hexstring2bytelist(self.networkPrefix.replace(':',''))
            dio             += self.dagRootEui64
        
        # calculate ICMPv6 checksum over ICMPv6header+ (RFC4443)
        checksum             = u.calculateCRC(dio[idxICMPv6:])
                               
        dio[idxICMPv6CS  ]   = checksum[0]
        dio[idxICMPv6CS+1]   = checksum[1]
        
        # log
        log.debug('sending DIO {0}'.format(self._formatByteList(dio)))
        
        # dispatch
        self.dispatch(
            signal          = 'bytesToMesh',
            data            =  (nextHop,dio)   #(''.join([chr(c) for c in nextHop]),''.join([chr(c) for c in dio])),
        )
        
        # schedule the next DIO transmission
        self._scheduleSendDIO(self.DIO_PERIOD)
    
    #======================== helpers =========================================
    
    def _formatByteList(self,l):
        '''
        \brief Format a bytelist into an easy-to-read string.
        
        That is:  [0xab,0xcd,0xef,0x00] -> '(4 bytes) ab-cd-ef-00'
        '''
        return '({0} bytes) {1}'.format(len(l),'-'.join(["%02x"%b for b in l]))
    
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
        