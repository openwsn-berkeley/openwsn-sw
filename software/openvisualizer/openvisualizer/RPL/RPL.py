# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
'''
Module which coordinates RPL DIO and DAO messages.

.. moduleauthor:: Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>
                  January 2013
.. moduleauthor:: Thomas Watteyne <watteyne@eecs.berkeley.edu>
                  April 2013
'''
import logging
log = logging.getLogger('RPL')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import struct
from datetime import datetime

from pydispatch import dispatcher

from openvisualizer.eventBus import eventBusClient
import SourceRoute
import openvisualizer.openvisualizer_utils as u

class RPL(eventBusClient.eventBusClient):
    
    _TARGET_INFORMATION_TYPE           = 0x05
    _TRANSIT_INFORMATION_TYPE          = 0x06
    
    # Period between successive DIOs, in seconds.
    DIO_PERIOD                         = 10
    
    ALL_RPL_NODES_MULTICAST            = [0xff,0x02]+[0x00]*13+[0x1a]
    
    # http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xml 
    IANA_ICMPv6_RPL_TYPE               = 155
    
    # RPL DIO (RFC6550)
    DIO_OPT_GROUNDED                   = 1<<7
    MOP_DIO_A                          = 1<<5
    MOP_DIO_B                          = 1<<4
    MOP_DIO_C                          = 1<<3
    PRF_DIO_A                          = 1<<2
    PRF_DIO_B                          = 1<<1
    PRF_DIO_C                          = 1<<0
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # store params
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'RPL',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'networkPrefix',
                    'callback'    : self._networkPrefix_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'infoDagRoot',
                    'callback'    : self._infoDagRoot_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getSourceRoute',
                    'callback'    : self._getSourceRoute_notif,
                },
            ]
        )
        
        # local variables
        self.stateLock            = threading.Lock()
        self.state                = {}
        self.networkPrefix        = None
        self.dagRootEui64         = None
        self.sourceRoute          = SourceRoute.SourceRoute()
        self.latencyStats         = {}
        
        # send a DIO periodically
        self._scheduleSendDIO(self.DIO_PERIOD) 
    
    #======================== public ==========================================
    
    def close(self):
        self.timer.cancel()
    
    #======================== private =========================================
    
    #==== handle EventBus notifications
    
    def _networkPrefix_notif(self,sender,signal,data):
        '''
        Record the network prefix.
        '''
        # store
        with self.stateLock:
            self.networkPrefix    = data[:]
    
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        Record the DAGroot's EUI64 address.
        '''
        
        eui64 = data['eui64'][:]
        
        # register if DAGroot
        if data['isDAGroot']==1 and self.networkPrefix:
            
            # log
            log.info("registering to DAGroot {0}".format(u.formatAddr(eui64)))
            
            # register
            self.register(
                sender            = self.WILDCARD,
                signal            = (
                    tuple(self.networkPrefix + eui64),
                    self.PROTO_ICMPv6,
                    self.IANA_ICMPv6_RPL_TYPE
                ),
                callback          = self._fromMoteDataLocal_notif,
            )
            
            # store DAGroot
            with self.stateLock:
                self.dagRootEui64 = data['eui64'][:]
        
        # unregister if not DAGroot
        if data['isDAGroot']==0:
            
            # log
            log.info("unregistering from DAGroot {0}".format(u.formatAddr(eui64)))
            
            # unregister from old DAGroot
            self.unregister(
                sender            = self.WILDCARD,
                signal            = (
                    tuple(self.networkPrefix + eui64),
                    self.PROTO_ICMPv6,
                    self.IANA_ICMPv6_RPL_TYPE
                ),
                callback          = self._fromMoteDataLocal_notif,
            )
            
            # clear DAGroot
            with self.stateLock:
                self.dagRootEui64 = None
    
    def _fromMoteDataLocal_notif(self,sender,signal,data):
        '''
        Called when receiving fromMote.data.local, probably a DAO.
        '''      
        # indicate data to topology
        self._indicateDAO(data)
        return True
    
    def _getSourceRoute_notif(self,sender,signal,data):
        destination = data
        return self.sourceRoute.getSourceRoute(destination)
    
    #===== send DIO
    
    def _scheduleSendDIO(self,interval):
        '''
        Schedule to send a DIO sometime in the future.
        
        :param interval: [in] In how many seconds the DIO is scheduled to be
            sent.
        '''
        self.timer      = threading.Timer(interval,self._cycleDIO)
        self.timer.name = 'DIO Timer'
        self.timer.start()
        
    def _cycleDIO(self):
        '''
        Send DIO and schedule next send.
        '''
        try:
            self._sendDIO()
        except Exception as err:
            errMsg=u.formatCriticalMessage(err)
            print errMsg
            log.critical(errMsg)
        finally:
            # Must ensure next send is scheduled
            self._scheduleSendDIO(self.DIO_PERIOD)
    
    def _sendDIO(self):
        '''
        Send a DIO.
        '''
        
        # don't send DIO if I didn't discover the DAGroot's EUI64
        if not self.dagRootEui64:
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
        idxNH                = len(dio)
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
            idxSrc           = len(dio) # this is a little hack as the source is the dodag
            dio             += self.networkPrefix
            dio             += self.dagRootEui64
        
        # wireshark calculates the IPv6 source and destination from the 
        # 6LoWPAN header. It is lot aware of the network prefix and uses
        # link-local addresses. We do the same in this implementation to avoid
        # checksum errors in Wireshark.
        wiresharkSrc         = [0xfe,0x80]+[0x00]*6+[dio[idxSrc+8]|0x02]+dio[idxSrc+9:idxSrc+16]
        wiresharkDst         = [
            0xfe,0x80,0x00,0x00,0x00,0x00,0x00,0x00,
            0x00,0x00,0x00,0xff,0xfe,0x00,0xff,0xff,
        ]
        
        # calculate ICMPv6 checksum over ICMPv6header+ (RFC4443)
        checksum             = u.calculatePseudoHeaderCRC(
            src              = wiresharkSrc,
            dst              = wiresharkDst,
            length           = [0x00,0x00,0x00,len(dio[idxICMPv6:])],
            nh               = [0x00]+dio[idxNH:idxNH+1],
            payload          = dio[idxICMPv6:],
        )
        
        dio[idxICMPv6CS  ]   = checksum[0]
        dio[idxICMPv6CS+1]   = checksum[1]
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug('sending DIO {0}'.format(u.formatBuf(dio)))

        # dispatch
        self.dispatch(
            signal           = 'bytesToMesh',
            data             = (nextHop,dio)
        )
    
    def _indicateDAO(self,tup):    
        '''
        Indicate a new DAO was received.
        
        This function parses the received packet, and if valid, updates the
        information needed to compute source routes.
        '''
        
        # retrieve source and destination
        try:
            source                = tup[0]
            if len(source)>8: 
                source=source[len(source)-8:]
            dao                   = tup[1]
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for destination and source".format(len(dao)))
            return
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output                = []
            output               += ['received DAO:']
            output               += ['- source :      {0}'.format(u.formatAddr(source))]
            output               += ['- dao :         {0}'.format(u.formatBuf(dao))]
            output                = '\n'.join(output)
            log.debug(output)
        
        # retrieve DAO header
        dao_header                = {}
        dao_transit_information   = {}
        dao_target_information    = {}
        
        try:
            # RPL header
            dao_header['RPL_InstanceID']    = dao[0]
            dao_header['RPL_flags']         = dao[1]
            dao_header['RPL_Reserved']      = dao[2]
            dao_header['RPL_DAO_Sequence']  = dao[3]
            # DODAGID
            dao_header['DODAGID']           = dao[4:20]
           
            dao                             = dao[20:]
            # retrieve transit information header and parents
            parents                         = []
            children                        = []
                          
            while (len(dao)>0):  
                if   dao[0]==self._TRANSIT_INFORMATION_TYPE: 
                    # transit information option
                    dao_transit_information['Transit_information_type']             = dao[0]
                    dao_transit_information['Transit_information_length']           = dao[1]
                    dao_transit_information['Transit_information_flags']            = dao[2]
                    dao_transit_information['Transit_information_path_control']     = dao[3]
                    dao_transit_information['Transit_information_path_sequence']    = dao[4]
                    dao_transit_information['Transit_information_path_lifetime']    = dao[5]
                    # address of the parent
                    prefix        =  dao[6:14]
                    parents      += [dao[14:22]]
                    dao           = dao[22:]
                elif dao[0]==self._TARGET_INFORMATION_TYPE:
                    dao_target_information['Target_information_type']               = dao[0]
                    dao_target_information['Target_information_length']             = dao[1]
                    dao_target_information['Target_information_flags']              = dao[2]
                    dao_target_information['Target_information_prefix_length']      = dao[3]
                    # address of the child
                    prefix        =  dao[4:12]
                    children     += [dao[12:20]]
                    dao           = dao[20:]
                else:
                    log.warning("DAO with wrong Option {0}. Neither Transit nor Target.".format(dao[0]))
                    return
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for DAO header".format(len(dao)))
            return
        
        # log
        output               = []
        output              += ['']
        output              += ['received RPL DAO from {0}'.format(u.formatAddr(source))]
        output              += ['- parents:']
        for p in parents:
            output          += ['   . {0}'.format(u.formatAddr(p))]
        output              += ['- children:']
        for p in children:
            output          += ['   . {0}'.format(u.formatAddr(p))]
        output               = '\n'.join(output)
        if log.isEnabledFor(logging.DEBUG):
            log.debug(output)
        print output
        
        # if you get here, the DAO was parsed correctly
        
        # update parents information with parents collected -- calls topology module.
        self.dispatch(          
            signal          = 'updateParents',
            data            =  (tuple(source),parents)  
        )
        
        #with self.dataLock:
        #    self.parents.update({tuple(source):parents})
   