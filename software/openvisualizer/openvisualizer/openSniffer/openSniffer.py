# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('openSniffer')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

from openvisualizer.eventBus import eventBusClient
import threading
import openvisualizer.openvisualizer_utils as u

#============================ parameters ======================================

class OpenSniffer(eventBusClient.eventBusClient):
    '''
    Class which is responsible for translating the packet received from Mote 
    to the wireshark.
    
    '''
    
    def __init__(self):
        
        # log
        log.info("create instance")
        
        # store params
        self.stateLock            = threading.Lock()
        self.networkPrefix        = None
        self.dagRootEui64         = None
         
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name             = 'OpenSniffer',
            registrations =  [
                {
                    'sender'   : self.WILDCARD, #signal when a pkt from sniffer
                    'signal'   : 'fromMote.packet',
                    'callback' : self._packetToWireshark, 
                },
            ]
        )
        
        # local variables
            
    #======================== public ==========================================
    
    #======================== private =========================================
    
    
    def _packetToWireshark(self,sender,signal,data):
        '''
        Converts a packet into wireshark format.
        
        '''

        print data
    
 
    
    #======================== helpers =========================================
    
    def _formatWireshark(self,pkt):
        NUM_BYTES_PER_LINE        = 16
        
        output                    = []
        index                     = 0
        while index<len(pkt):
            this_line             = []
            
            # get the bytes for this line
            bytes                 = pkt[index:index+NUM_BYTES_PER_LINE]
            
            # print the header
            this_line            += ['%06x '%index]
            
            # print the bytes (gather the end_chars)
            end_chars             = []
            end_chars            += ['  ']
            for b in bytes:
                # print the bytes
                this_line        += [' %02x'%b]
                # gather the end_chars
                if b>32 and b<127:
                    end_chars    += [chr(b)]
                else:
                    end_chars    += ['.']
            
            # pad
            for _ in range(len(bytes),NUM_BYTES_PER_LINE):
                this_line        += ['   ']
            
            # print the end_chars
            this_line            += end_chars
            
            # store the line
            this_line             = ''.join(this_line)
            output               += [this_line]
            
            # increment index
            index                += NUM_BYTES_PER_LINE
        
        return '\n'.join(output)
