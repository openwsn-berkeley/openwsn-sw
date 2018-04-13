# Copyright (c) 2010-2013, Regents of the University of California.
# All rights reserved.
#
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
import threading
import json
from Queue import Queue

import zmq
from pydispatch import dispatcher

log = logging.getLogger('remoteConnectorServer')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())


class remoteConnectorServer(object):
    def __init__(self,
                 zmq_admin_port=50001,
                 zmq_pub_port=50000,
                 zmq_pub_all_port=50002,
                 zmq_inject_port=60000):

        # log
        log.info("creating instance")

        # local variables
        self.zmq_admin_port = zmq_admin_port
        self.zmq_pub_port = zmq_pub_port
        self.zmq_pub_all_port = zmq_pub_all_port
        self.zmq_inject_port = zmq_inject_port
        self.roverdict = {}
        self.stateLock = threading.Lock()
        self.networkPrefix = None
        self._subcribedDataForDagRoot = False

        # give this thread a name
        self.name = 'remoteConnectorServer'

        # initiate ZeroMQ connection
        self.context = zmq.Context()
        # Required to have a thread-safe medium between the pub_all thread and the other threads
        # that will call pydispatcher
        self.queue = Queue()

        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.setsockopt(zmq.IPV6, 1)
        self.publisher.setsockopt(zmq.IPV4ONLY, 0)
        self.pub_address = "tcp://*:%d" % self.zmq_pub_port
        self.publisher.bind(self.pub_address)
        log.info('Publisher started on %s' % self.pub_address)

        self.threads = [threading.Thread(target=self._handle_sub),
                        threading.Thread(target=self._handle_req),
                        threading.Thread(target=self._handle_pub_all),
                        threading.Thread(target=self._handle_admin)]

        for thread in self.threads:
            thread.setDaemon(True)
            thread.start()

    # ======================== eventBus interaction ============================

    def _sendToRemote_handler(self, sender, signal, data):

        self.publisher.send_json({'sender': sender,
                                  'signal': signal,
                                  'data': data.encode('hex')})
        log.info('Message sent: sender: ' + sender, 'signal: ' + signal, 'data: ' + data.encode('hex'))

    def _handle_pub_all(self):
        """
        Create the pub_all socket and consume messages from the internal queue.

        :return:
        """
        context = zmq.Context()
        pub_all = context.socket(zmq.PUB)
        pub_all.setsockopt(zmq.IPV6, 1)
        pub_all.setsockopt(zmq.IPV4ONLY, 0)
        pub_all_address = "tcp://*:%d" % self.zmq_pub_all_port
        pub_all.bind(pub_all_address)
        log.info('Publisher all started on %s' % pub_all_address)

        while True:
            event = self.queue.get(block=True)
            pub_all.send_json(event)

    def clean_event(self, raw_event):
        """
        Convert a data tuple pydispatcher event to a dict
        before sending it on the rover socket
        """
        event = raw_event
        try:
            event["data"] = event.get("data", None)._asdict()
        except AttributeError:
            log.debug("The data was not a tuple")
        return event

    def _handle_admin(self):
        """
        Manage pub settings of the ZMQ PUB socket.

        :return: the current list of signal triggering the PUB socket
        """
        context = zmq.Context()
        admin = context.socket(zmq.REP)
        admin.setsockopt(zmq.IPV6, 1)
        admin.setsockopt(zmq.IPV4ONLY, 0)
        admin.bind("tcp://*:%s" % self.zmq_admin_port)

        def _handle_pub_all_callback(**kwargs):
            # Assume here that we got a JSON
            cleaned_event = self.clean_event(kwargs)
            self.queue.put(cleaned_event)

        subscriptions = set()
        while True:
            #  Wait for next request from client
            message = admin.recv()
            log.info("Received request: %s" % message)

            try:
                message = json.loads(message)
            except Exception as e:
                print("That was not a JSON")
                log.error(e)
                continue

            if not set(message.keys()).issubset({"sub", "unsub"}):
                admin.send_json({"error": "Incorrect format use a JSON with sub, unsub"})
                continue
            count = 0
            if "sub" in message.keys():
                for sub in message["sub"]:
                    if sub not in subscriptions:
                        dispatcher.connect(_handle_pub_all_callback, signal=sub)
                        count += 1
                        subscriptions.add(sub)
            if "unsub" in message.keys():
                for unsub in message["unsub"]:
                    if unsub in subscriptions:
                        dispatcher.disconnect(_handle_pub_all_callback, signal=unsub)
                        count += 1
                        subscriptions.remove(unsub)
            admin.send_json({"subscriptions": list(subscriptions)})

    def _handle_sub(self):
        """

        :return:
        """
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.setsockopt(zmq.IPV6, 1)
        self.subscriber.setsockopt(zmq.IPV4ONLY, 0)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "")
        log.info("Subscriber started")

        count = 0
        while True:
            event = self.subscriber.recv_json()
            for i in range(len(event['data'])):
                dispatcher.send(
                    sender=event['sender'].encode("utf8"),
                    signal=event['signal'].encode("utf8"),
                    data=event['data'][i]
                )

    def _handle_req(self):
        """
        Function call when external event are injected in the message bus
        :return:
        """
        context = zmq.Context()
        rep_socket = context.socket(zmq.REP)
        rep_socket.setsockopt(zmq.IPV6, 1)
        rep_socket.setsockopt(zmq.IPV4ONLY, 0)
        rep_address = "tcp://*:%d" % self.zmq_inject_port
        rep_socket.bind(rep_address)
        log.info("ZMQ REP socket started on %s" % rep_address)

        while True:
            event = rep_socket.recv_json()
            if not set(event.keys()).issuperset({"sender", "signal", "data"}):
                error = {"error": "Incorrect format use a JSON with sender, signal and data"}
                rep_socket.send_json(error)
                log.error(error)
                continue

            log.info("Received remote event\n" + json.dumps(event) + "\nDispatching to event bus")
            dispatcher.send(
                sender=event["sender"].encode("utf8"),
                signal=event["signal"].encode("utf8"),
                data=event["data"]
            )
            rep_socket.send_json({"status": "ok"})

    # ======================== public ==========================================

    def quit(self):
        raise NotImplementedError()

    def initRoverConn(self, newroverdict):
        # clear history
        dispatcher.disconnect(self._sendToRemote_handler)
        while len(self.roverdict) > 0:
            for oldIP in self.roverdict.keys():
                self.subscriber.disconnect("tcp://%s:%s" % (oldIP, self.zmq_pub_port))
                self.roverdict.pop(oldIP)

        # add new configuration
        self.roverdict = newroverdict.copy()
        log.info('Rover connection:', str(self.roverdict))
        for roverIP, value in self.roverdict.items():
            if not isinstance(value, str):
                self.subscriber.connect("tcp://%s:%s" % (roverIP, self.zmq_pub_port))
                for serial in self.roverdict[roverIP]:
                    signal = 'fromMoteConnector@' + serial
                    dispatcher.connect(
                        self._sendToRemote_handler,
                        signal=signal.encode('utf8')
                    )
            else:
                self.roverdict.pop(roverIP)

    def closeRoverConn(self, ipAddr):
        if ipAddr in self.roverdict.keys():
            self.subscriber.disconnect("tcp://%s:%s" % (ipAddr, self.zmq_pub_port))
            self.roverdict.pop(ipAddr)
