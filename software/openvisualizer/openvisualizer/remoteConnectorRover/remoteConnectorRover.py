# Copyright (c) 2010-2013, Regents of the University of California.
# All rights reserved.
#
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('remoteConnectorRover')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import zmq

from pydispatch import dispatcher


class remoteConnectorRover():


    def __init__(self, app, PCip, PCport, roverID):
        # log
        log.info("creating instance")

        # local variables
        self.stateLock                 = threading.Lock()
        self.PCip                      = PCip
        self.PCport                    = PCport
        self.roverID                   = roverID
        self.goOn                      = True


        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        #Always start the publisher on the same port as the PC (choice)
        self.publisher.setsockopt(zmq.IPV6, 1)
        self.publisher.setsockopt(zmq.IPV4ONLY, 0)
        self.publisher.bind("tcp://*:{0}".format(self.PCport))
        log.info('publisher started')

        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.setsockopt(zmq.IPV6, 1)
        self.subscriber.setsockopt(zmq.IPV4ONLY, 0) #needed on old pyzmq versions
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")
        self.subscriber.connect("tcp://%s:%s" % (self.PCip, self.PCport))
        #set timeout on receiving so the thread can terminate when self.goOn == False.
        self.subscriber.setsockopt(zmq.RCVTIMEO, 1000)

        # give this thread a name
        self.name = 'remoteConnectorRover'

        for mote in app.getMoteProbes() :
            # subscribe to dispatcher
            dispatcher.connect(
                self._sendToRemote_handler,
                signal = 'fromMoteProbe@'+mote.getPortName(),
            )

        self.t = threading.Thread(target=self._recvdFromRemote)
        self.t.setDaemon(True)
        self.t.start()
        log.info('subscriber started')


    #======================== remote interaction ============================
    def _sendToRemote_handler(self,sender,signal,data):
        #send the data after appending @roverID
        self.publisher.send_json({'sender' : '{0}@{1}'.format(sender,self.roverID), 'signal' : '{0}@{1}'.format(signal,self.roverID), 'data':data})
        log.debug('message sent to remote host :\n sender : {0}, signal : {1}, data : {2}'.format('{0}@{1}'.format(sender,self.roverID), '{0}@{1}'.format(signal,self.roverID), data))

    def _recvdFromRemote(self):
        while self.goOn :
            try :
                event = self.subscriber.recv_json()
                log.debug("\nReceived remote command\n"+event['data']+"from sender : "+event['sender']+"\nDispatching to event bus")
                signal = event['signal']
                sender = event['sender']
                # check that it is for this rover
                if signal.endswith('@{0}'.format(self.roverID)) and sender.endswith('@{0}'.format(self.roverID)) :
                    #remove the roverID
                    signal = signal[:-(len(self.roverID)+1)]
                    sender = sender[:-(len(self.roverID)+1)]
                    #Python 2 and strings...
                    signal.encode("utf8")
                    sender.encode("utf8")
                    dispatcher.send(signal=signal, sender=sender, data=event['data'].decode("hex"))
            except zmq.Again :
                pass

    #======================== public ==========================================

    def close(self):
        self.goOn = False