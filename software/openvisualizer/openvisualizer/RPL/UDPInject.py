# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
'''
Module which receives UDP Latency messages .

.. moduleauthor:: Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>
                  April 2013
'''
import logging
log = logging.getLogger('udpInject')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import struct

import threading
import openvisualizer.openvisualizer_utils as u
from   datetime import datetime

from openvisualizer.eventBus import eventBusClient

#import math

class UDPInject(eventBusClient.eventBusClient):
   
    UDP_INJECT_PORT  = 61617 # 0xf0b1
    
    def __init__(self):
                # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'UDPInject',
            registrations         =  [
               {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'infoDagRoot',
                    'callback'    : self._infoDagRoot_notif,
                },
            ]
        )

        # local variables
        self.stateLock          = threading.Lock()
        self.destinationAddress = []
        self.registered         = False
        self.contentStats       = {}
        
    
    #======================== public ==========================================
    #Triggered by parser data as a hack 
    def _inject_notif(self,sender,signal,data):
        '''
        This method is invoked whenever a UDP packet is send from a mote from
        UDPInject application. This application listens at port 61617 and 
        computes the latency of a packet. Note that this app is crosslayer
        since the mote sends the data within a UDP packet and OpenVisualizer
        (ParserData) handles that packet and reads UDP payload to compute time
        difference.
        
        At the bridge module on the DAGroot, the ASN of the DAGroot is appended
        to the serial port to be able to know what is the ASN at reception
        side.
        
        Calculate latency values are in ms[SUPERFRAMELENGTH].
        '''
        address    = ",".join(hex(c) for c in data[0])
        asn        = struct.unpack('<HHB',''.join([chr(c) for c in data[1][:5]]))
        counter    = struct.unpack('<H',''.join([chr(c) for c in data[1][5:7]]))

        stats = {}
        
        # these fields are common
        stats.update({'asn'    :asn})
        stats.update({'counter':counter})
        
        # add to dictionary and compute stats...
        self.stateLock.acquire()
        self.contentStats.update({str(address):stats})
        self.stateLock.release()

        # print self.contentStats

        return True

    # this is not activated as this function are not bound to a signal
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        Record the DAGroot's EUI64 address.
        '''

        if not self.registered:
        
            networkPrefix = self._dispatchAndGetResult(
                signal       = 'getNetworkPrefix',
                data         = [],
            )
            networkHost   = self._dispatchAndGetResult(
                signal       = 'getNetworkHost',
                data         = [],
            )
            self.destinationAddress = networkPrefix + networkHost
            # signal to which this component is subscribed.
            signal=(tuple(self.destinationAddress),self.PROTO_UDP,self.UDP_INJECT_PORT)
            
            # register
            self.register(
                sender   = self.WILDCARD,
                signal   = signal,
                callback = self._inject_notif,
            )

            self.registered = True
    
    def _calculatePLR(self, rcvdPkt, sentPkt):
        '''
        Calculate Packet Loss Ratio for the sender.
        '''
        return float(sentPkt-rcvdPkt)/sentPkt*100
        
        
        
    
    #===== formatting
    
    def _formatUDPInjectStat(self, stats, str):
        
        output  = []
        output += ['']
        output += ['']
        output += ['============================= UDPInject statistics =============================']
        output += ['']
        output += ['Mote address:             {0}'.format(str)]
        output += ['Min latency:              {0}ms'.format(stats.get('min'))]
        output += ['Max latency:              {0}ms'.format(stats.get('max'))]
        output += ['Packets received:         {0}'.format(stats.get('pktRcvd'))]
        output += ['Packets sent:             {0}'.format(stats.get('pktSent'))]
        output += ['Avg latency:              {0}ms'.format(stats.get('avg'))]
        output += ['Latest latency:           {0}ms'.format(stats.get('lastVal'))]
        output += ['Preferred parent:         {0}'.format(stats.get('prefParent'))]
        output += ['Sequence Number:          {0}'.format(stats.get('SN'))]
        output += ['Duplicated packets:       {0}'.format(stats.get('DUP'))]
        output += ['PLR:                      {0}%'.format(stats.get('PLR'))]
        output += ['Received:                 {0}'.format(stats.get('lastMsg'))]
        output += ['']
        output += ['']
        return '\n'.join(output)
