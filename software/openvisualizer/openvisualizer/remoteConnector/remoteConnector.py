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
import json
import zmq

from pydispatch import dispatcher


class remoteConnector():

    def __init__(self, zmqport=50000):
        
        # log
        log.info("creating instance")

        # local variables
        self.zmqport                   = zmqport
        self.roverlist                 = {}
        self.stateLock                 = threading.Lock()
        self.networkPrefix             = None
        self._subcribedDataForDagRoot  = False

        # give this thread a name
        self.name = 'remoteConnector'

        # initiate ZeroMQ connection
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:%d" % self.zmqport)
        self.subscriber = context.socket(zmq.SUB)
        print '====Publisher started'

        self.threads = []
        t = threading.Thread(target=self._recvdFromRemote)
        t.setDaemon(True)
        t.start()
        self.threads.append(t)

        
    #======================== eventBus interaction ============================
    
    def _sendToRemote_handler(self,sender, signal, data):

        self.publisher.send_json({'sender' : sender, 'signal' : signal, 'data': data.encode('hex')})
        print '\nMessage sent: sender: ' + sender, 'signal: ' + signal, 'data: '+ data.encode('hex')


    def _recvdFromRemote(self):
        count=0
        while True:
            event = self.subscriber.recv_json()
            if count > 10:
                print "\nReceived remote event\n"+json.dumps(event)+"\nDispatching to event bus\n"
                count=0
            dispatcher.send(
                sender  =  event['sender'].encode("utf8"),
                signal  =  event['signal'].encode("utf8"),
                data    =  event['data']
            )
            count+=1


    
    #======================== public ==========================================
    
    def quit(self):
        raise NotImplementedError()

    def initRoverConn(self, newroverlist):
        # clear history
        dispatcher.disconnect(self._sendToRemote_handler)
        while len(self.roverlist)>0:
            for oldIP in self.roverlist.keys():
                self.subscriber.disconnect("tcp://%s:%s" % (oldIP, self.zmqport))
                print "====Clearing historical connections: ",oldIP
                self.roverlist.pop(oldIP)


        # add new configuration
        self.roverlist = newroverlist.copy()
        print '====Subscription thread:', str(self.threads)
        print '    Initiating rover connection:'+ str(self.roverlist)
        for roverIP in self.roverlist.keys():
            self.subscriber.connect("tcp://%s:%s" % (roverIP, self.zmqport))
            self.subscriber.setsockopt(zmq.SUBSCRIBE, "")
            print '    Subscriber connected to TCP://'+ str(roverIP) +":"+ str(self.zmqport)
            for serial in self.roverlist[roverIP]:
                signal = 'fromMoteConnector@'+serial
                dispatcher.connect(
                    self._sendToRemote_handler,
                    signal = signal.encode('utf8')
                    )
