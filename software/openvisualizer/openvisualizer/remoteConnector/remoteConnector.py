# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('remoteConnector')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import socket
import traceback
import sys
import json
import openvisualizer.openvisualizer_utils as u
import zmq
import time

from pydispatch import dispatcher
from openvisualizer.eventBus      import eventBusClient
from openvisualizer.moteState     import moteState


class remoteConnector(eventBusClient.eventBusClient):

    def __init__(self, roverlist=[], PUBport=50000):
        
        # log
        log.info("creating instance")

        # local variables
        self.stateLock                 = threading.Lock()
        self.networkPrefix             = None
        self._subcribedDataForDagRoot  = False

        self.roverlist = roverlist
        self.SUBport = PUBport

        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:%d" % PUBport)
        print 'publisher started'


        self.subscriber = context.socket(zmq.SUB)

        #For test
        roverPort = 50000
        self.addRover('localhost')

        for roverIP in roverlist:
            self.subscriber.connect("tcp://%s:%s" % (roverIP, roverPort))
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")

        # give this thread a name
        self.name = 'remoteConnector'
       
        eventBusClient.eventBusClient.__init__(
            self,
            name             = self.name,
            registrations =  [
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'infoDagRoot',
                    'callback' : self._sendToRemote_handler,
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'cmdToMote',
                    'callback' : self._sendToRemote_handler,
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'bytesToMesh',
                    'callback' : self._sendToRemote_handler,
                },
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'dispatchtest',
                    'callback' : self._dispatchtest,
                }
            ]
        )

        # subscribe to dispatcher

        t = threading.Thread(target=self._recvdFromRemote)
        t.setDaemon(True)
        t.start()
        print 'subscriber started'
        
    #======================== eventBus interaction ============================
    
    def _sendToRemote_handler(self,sender,signal,data):
        self.publisher.send_json({'sender' : sender, 'signal' : signal, 'data':data})
        print 'msg sent'

    def _recvdFromRemote(self):
        while True:
           event = self.subscriber.recv_json()
           print "\nReceived remote event\n"+json.dumps(event)+"\nDispatching to event bus\n"
           self.dispatch('dispatchtest', event['data'])

    def _dispatchtest(self,sender,signal,data):
        print '\n\nDispatch Test succeed, received dispatched event from evenbus:\n'
        print 'sender: ' + sender, 'signal:' + signal, 'data: '+str(data)

    
    #======================== public ==========================================
    
    def quit(self):
        raise NotImplementedError()

    def addRover(self, roverIP):
        self.roverlist.append(roverIP)
