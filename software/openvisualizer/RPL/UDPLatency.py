'''
\brief Module which receives UDP Latency messages .

\author Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>, April 2013.

'''

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('udpLatency')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import openvisualizer_utils as u
from   datetime import datetime

from eventBus import eventBusClient

class UDPLatency(eventBusClient.eventBusClient):
   
    UDP_LATENCY_PORT  = 61001
    
    def __init__(self):
                # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'UDPLatency',
            registrations         =  [
               {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'latency',
                    'callback'    : self._latency_notif,
                },
            ]
        )

        # local variables
        self.stateLock       = threading.Lock()
        self.latencyStats    = {}
        
    
    #======================== public ==========================================
    #Triggered by parser data as a hack 
    def _latency_notif(self,sender,signal,data):
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
        address    = ",".join(hex(c) for c in data[0])
        latency    = data[1]
        parent     = ",".join(hex(c) for c in data[2])
        
        stats      = {} #dictionary of stats
        
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
        
        #add to dictionary and compute stats...
        self.stateLock.acquire()  
        self.latencyStats.update({str(address):stats}) 
        self.stateLock.release()
        
        #log stats 
        log.debug(self._formatUDPLatencyStat(self.latencyStats.get(str(address)), str(address)))
    
    
    
    #this is not activated as this functiona are not bound to a signal
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        \brief Record the DAGroot's EUI64 address.
        '''
        with self.stateLock:
            self.dagRootEui64     = []
            for c in data['eui64']:
                self.dagRootEui64     +=[int(c)]
        #signal to which this component is subscribed.
        signal=(self.networkPrefix + self.dagRootEui64,self.PROTO_UDP,self.UDP_LATENCY_PORT)
        
        #register as soon as I get an address
        self._register(self,self.WILDCARD,signal,self._latency_notif)    
         
    def _networkPrefix_notif(self,sender,signal,data):
        '''
        \brief Record the network prefix.
        '''
        with self.stateLock:
            self.networkPrefix    = data



    #===== formatting
    def _formatUDPLatencyStat(self,stats, str):
        
        output  = []
        output += ['']
        output += ['']
        output += ['============================= UDPLatency statistics =============================']
        output += ['Mote address:          {0}'.format(str)]
        output += ['Min latency:           {0}'.format(stats.get('min'))]
        output += ['Max latency:           {0}'.format(stats.get('max'))]
        output += ['Num packets:           {0}'.format(stats.get('num'))]
        output += ['Avg latency:           {0}'.format(stats.get('avg'))]
        output += ['Latest latency:        {0}'.format(stats.get('lastVal'))]
        output += ['Preferred parent:      {0}'.format(stats.get('prefParent'))]
        output += ['Received:              {0}'.format(stats.get('lastMsg'))]
        output += ['']
        return '\n'.join(output)
