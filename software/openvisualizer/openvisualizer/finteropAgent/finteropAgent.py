# Copyright (c) 2010-2013, Regents of the University of California.
# All rights reserved.
#
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging

log = logging.getLogger('finteropAgent')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import threading
import copy
import json
import binascii
import pika
import sys

from openvisualizer.moteState   import moteState
from openvisualizer.eventBus    import eventBusClient
from openvisualizer.eventBus    import eventBusMonitor
import threading

AMQP_URL = 'amqp://YKGG2QQ5:7WULNVMN@mq.dev.f-interop.eu:443/a717a5cf-7c97-455e-8ffe-d25308bfe2f9'

class finteropAgent(eventBusClient.eventBusClient):

    HEXDUMP_LINE_MAXNUMBER = 20
    HEXDUMP_LINE_LENGTH = 16

    def __init__(self):

        # log
        log.info("create instance")

        self.serialPortRole = {}

        # store params
        self.exchange = "amq.topic"
        self.properties = pika.BasicProperties(content_type='text/plain', delivery_mode=1)


        # create channel for publishing
        self.routing_key = "sniffer.data"
        self.sniffer_connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        self.sniffer_channel = self.sniffer_connection.channel()
        self.sniffer_channel.confirm_delivery()

        self.mapping = {
            # "control.testsuite.finish": self.handle_testsuite_finish,

            "agent.6p_add":self.handle_6p_add,
            "agent.6p_count":self.handle_6p_count,
            "agent.6p_relocate":self.handle_6p_relocate,
            "agent.6p_clear":self.handle_6p_clear,
            "agent.6p_delete":self.handle_6p_delete,
            "agent.6p_list":self.handle_6p_list,

            "agent.synced":self.handle_synced,

            "agent.set_channel":self.handle_set_channel,
        }

        # create channel for consuming
        self._connection = pika.BlockingConnection(pika.URLParameters(AMQP_URL))
        self._channel = self._connection.channel()

        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name             = 'finteropAgent',
            registrations =  [
                {
                    'sender'   : self.WILDCARD, #signal from internet to the mesh network
                    'signal'   : 'fromMote.sniffedPacket',
                    'callback' : self._sniffedPacketNotification
                },
            ]
        )

    # ======================== private =========================================

    def __enter__(self):
        self.bootstrap()
        return self

    def bootstrap(self, ):
        # Binding of all routing keys to a given queue
        for key, handler in self.mapping.items():
            queue_name = self.amqp_name + " | " + key
            # Creation of the queue
            self._channel.queue_declare(queue=queue_name,
                                        auto_delete=True)

            self._channel.queue_bind(queue=queue_name,
                                     routing_key=key,
                                     exchange=self.exchange)

            # Add callback to the queue
            self._channel.basic_consume(queue=queue_name,
                                        consumer_callback=handler)
            print("%s: Binding %s to %s" % (self.amqp_name, queue_name, handler))

    def setSerialPortRole(self,dagroot,sniffer,node):

        self.serialPortRole['node']     = node
        self.serialPortRole['dagroot']  = dagroot
        self.serialPortRole['sniffer']  = sniffer

        print self.serialPortRole


    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        start consuming.

        """
        self._channel.start_consuming()

    def _sniffedPacketNotification(self, signal, sender, data):
        '''
        only Process signal 'fromMote.sniffedPacket' mode
        '''

        body = data[0:-3]
        crc = data[-3:-1]
        frequency = data[-1]

        # wrap with zep header
        zep    = eventBusMonitor.eventBusMonitor()._wrapZepCrc(body, frequency)

        udp = [
            0x00, 0x00,  # source port
            0x45, 0x5a,  # destination port
            0x00, 8 + len(zep),  # length
            0xbc, 0x04,  # checksum
        ]

        ipv6 = [
            0x60,  # version
            0x00, 0x00, 0x00,  # traffic class
            0x00, len(udp) + len(zep),  # payload length
            0x11,  # next header (17==UDP)
            0x08,  # HLIM
            0xbb, 0xbb, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x01,  # src
            0xbb, 0xbb, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x01,  # dest
        ]

        ethernet = [
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # source
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # destination
            0x86, 0xdd,  # type (IPv6)
        ]

        hex_dump = self.convert_to_hexdump(ethernet + ipv6 + udp + zep)
        msg_body = json.dumps({"format": "hexdump","raw_ip": False,"value": hex_dump})

        self.notify(msg_body, False)

        print msg_body


    def notify(self, msg_body, mandatory=False):
        """
        :param message:
        :param mandatory:
        :return:
        """

        if self.sniffer_channel.basic_publish(exchange=self.exchange,
                                 routing_key=self.routing_key,
                                 body=msg_body,
                                 mandatory=mandatory,
                                 properties=self.properties) or not mandatory:
            log.debug('Message publish was confirmed')
            return True
        else:
            log.error("Hum something went wrong with message: %s" % message)
            log.error('Message could not be confirmed')
            log.error("Mandatory: %s" % mandatory)
            return False

    def convert_to_hexdump(self, frame):

        hexdump = ''
        for i in range(self.HEXDUMP_LINE_MAXNUMBER):
            hexdump += '0{:02x}0 '.format(i)
            if len(frame) > self.HEXDUMP_LINE_LENGTH * (i + 1):
                hexdump += ''.join(
                    '{:02x} '.format(x) for x in frame[self.HEXDUMP_LINE_LENGTH * i:self.HEXDUMP_LINE_LENGTH * (i + 1)])
                hexdump += '\n'
            else:
                hexdump += ''.join('{:02x} '.format(x) for x in frame[self.HEXDUMP_LINE_LENGTH * i:])
                hexdump += '\n'
                break

        return hexdump

    # ======================== amqp handler =========================================

    def _validate_json(body):
        try:
            return json.loads(body)
        except ValueError:
            return None

    def handle_6p_add(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "cell_option": "tx",
            "num_cells": 2,
            "candidate_list_slot": [4, 5],
            "candidate_list_channel": [4, 5]
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        allowed_roles = ("dag_root", "node")
        if data.get("role", "") not in allowed_roles:
            print("Role not in %s" % str(allowed_roles))
            return
        role = data["role"]

        try:
            num_cells = data["num_cells"]
        except KeyError:
            return

        cell_options_allowed = ("rx", "tx", "shared")
        try:
            cell_option = data["cell_option"]
            assert cell_option in cell_options_allowed
        except KeyError:
            return
        except AssertionError:
            print("Cell option not in %s" % str(cell_options_allowed))
            return

        try:
            candidate_list_slot = data["candidate_list_slot"]
        except KeyError:
            return

        try:
            candidate_list_channel = data["candidate_list_channel"]
        except KeyError:
            return

        command = '6pAdd'
        parameter = '{0},{1},{2},{3}'.format(
            cell_option, num_cells,
            '-'.join(str(slot) for slot in candidate_list_slot),
            '-'.join(str(slot) for slot in candidate_list_channel)
        )
        
        self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    def handle_6p_count(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "cell_option": "tx",
            "num_cells": 2,
            "candidate_list_slot": [4, 5],
            "candidate_list_channel": []
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        cell_options_allowed = ("rx", "tx", "shared")
        try:
            cell_option = data["cell_option"]
            assert cell_option in cell_options_allowed
        except KeyError:
            return
        except AssertionError:
            print("Cell option not in %s" % str(cell_options_allowed))
            return

        allowed_roles = ("dag_root", "node")
        if data.get("role", "") not in allowed_roles:
            print("Role not in %s" % str(allowed_roles))
            return
        role = data["role"]

        command   = '6pCount'
        parameter = '{0}'.format(cell_option)
        
        self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    def handle_synced(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

    def handle_6p_clear(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "role": "node"
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        allowed_roles = ("dag_root", "node")
        if data.get("role", "") not in allowed_roles:
            print("Role not in %s" % str(allowed_roles))
            return
        role = data["role"]

        command   = '6pClear'
        parameter = 'all'
        
        self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    def handle_6p_list(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "cell_option": "tx",
            "num_cells": 2,
            "candidate_list_slot": [4, 5],
            "candidate_list_channel": []
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        cell_options_allowed = ("rx", "tx", "shared")
        try:
            cell_option = data["cell_option"]
            assert cell_option in cell_options_allowed
        except KeyError:
            return
        except AssertionError:
            print("Cell option not in %s" % str(cell_options_allowed))
            return

        allowed_roles = ("dag_root", "node")
        if data.get("role", "") not in allowed_roles:
            print("Role not in %s" % str(allowed_roles))
            return
        role = data["role"]

        try:
            list_offset = data["list_offset"]
        except KeyError:
            return

        try:
            max_list_length = data["max_list_length"]
        except KeyError:
            return

        command   = '6pList'
        parameter = '{0},{1},{2}'.format(cell_option, list_offset, max_list_length)
        
        self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    def handle_6p_delete(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "role": "node",
            "cell_option": "tx",
            "num_cells": 2,
            "candidate_list_slot": [4, 5],
            "candidate_list_channel": []
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        cell_options_allowed = ("rx", "tx", "shared")
        try:
            cell_option = data["cell_option"]
            assert cell_option in cell_options_allowed
        except KeyError:
            return
        except AssertionError:
            print("Cell option not in %s" % str(cell_options_allowed))
            return

        allowed_roles = ("dag_root", "node")
        try:
            role = data["role"]
            assert role in allowed_roles
        except KeyError:
            return
        except AssertionError:
            print("Role not in %s" % str(allowed_roles))
            return

        try:
            num_cells = data["num_cells"]
        except KeyError:
            return

        try:
            candidate_list_slot = data["candidate_list_slot"]
        except KeyError:
            return

        try:
            candidate_list_channel = data["candidate_list_channel"]
        except KeyError:
            return

        command   = '6pDelete'
        parameter = '{0},{1},{2},{3}'.format(
            cell_option, num_cells,
            '-'.join(str(slot) for slot in candidate_list_slot),
            '-'.join(str(slot) for slot in candidate_list_channel)
        )
        
        self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    def handle_6p_relocate(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "role": "node"
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        allowed_roles = ("dag_root", "node")
        try:
            role = data["role"]
            assert role in allowed_roles
        except KeyError:
            return
        except AssertionError:
            print("Role not in %s" % str(allowed_roles))
            return

        cell_options_allowed = ("rx", "tx", "shared")
        try:
            cell_option = data["cell_option"]
            assert cell_option in cell_options_allowed
        except KeyError:
            return
        except AssertionError:
            print("Cell option not in %s" % str(cell_options_allowed))
            return

        try:
            num_cells = data["num_cells"]
        except KeyError:
            return

        try:
            candidate_delete_list_slot = data["candidate_delete_list_slot"]
        except KeyError:
            return

        try:
            candidate_delete_list_channel = data["candidate_delete_list_channel"]
        except KeyError:
            return

        try:
            candidate_add_list_slot = data["candidate_add_list_slot"]
        except KeyError:
            return

        try:
            candidate_add_list_channel = data["candidate_add_list_channel"]
        except KeyError:
            return

        command   = '6pRelocate'
        parameter = '{0},{1},{2},{3},{4},{5}'.format(
            cell_option, num_cells,
            '-'.join(str(slot) for slot in candidate_delete_list_slot),
            '-'.join(str(slot) for slot in candidate_delete_list_channel),
            '-'.join(str(slot) for slot in candidate_add_list_slot),
            '-'.join(str(slot) for slot in candidate_add_list_channel)
        )
        
        self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    def handle_set_channel(self, channel, method, properties, body):
        """

        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:

        Expected format:

        {
            "channel": 20
        }
        """
        data = self._validate_json(body=body)
        if data is None:
            print("JSON decoding error: %s" % body)
            return

        allowed_channel = range(11, 27)
        try:
            wpan_channel = data["channel"]
            assert wpan_channel in allowed_channel
        except KeyError:
            return
        except AssertionError:
            print("Channel not in %s" % str(allowed_channel))
            return

        for mote in self.mote_probes.values():
            command   = 'channel'
            parameter = '{0}'.format(wpan_channel)
        
            self._sendCommand(self.serialPortRole[role],[moteState.moteState.SET_COMMAND,command,parameter])

    # ======================== amqp handler =========================================

    def _sendCommand(self,serialport,action):
        
        # dispatch
        self.dispatch(
            signal        = 'cmdToMote',
            data          = {
                                'serialPort':    serialport,
                                'action':        action,
                            },
        )