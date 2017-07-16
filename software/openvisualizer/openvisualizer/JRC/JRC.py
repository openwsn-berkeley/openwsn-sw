import threading
from   coap   import    coap,                    \
                        coapResource,            \
                        coapDefines as d,        \
                        coapOption as o,         \
                        coapUtils as u,          \
                        coapObjectSecurity as oscoap

import coseDefines
import logging.handlers
try:
    from openvisualizer.eventBus import eventBusClient
    import openvisualizer.openvisualizer_utils
except ImportError:
    pass

log = logging.getLogger('JRC')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import cbor
import binascii
import os

# ======================== Top Level JRC Class =============================
class JRC():
    def __init__(self):
        coapResource = joinResource()
        self.coapServer = coapServer(coapResource, contextHandler(coapResource).securityContextLookup)

    def close(self):
        self.coapServer.close()

# ======================== Security Context Handler =========================
class contextHandler():
    MASTERSECRET = binascii.unhexlify('000102030405060708090A0B0C0D0E0F')

    def __init__(self, joinResource):
        self.joinResource = joinResource

    # ======================== Context Handler needs to be registered =============================
    def securityContextLookup(self, kid):
        kidBuf = u.str2buf(kid)

        eui64 = kidBuf[:-1]
        senderID = eui64 + [0x01]  # sender ID of JRC is reversed
        recipientID = eui64 + [0x00]

        # if eui-64 is found in the list of joined nodes, return the appropriate context
        # this is important for replay protection
        for dict in self.joinResource.joinedNodes:
            if dict['eui64'] == u.buf2str(eui64):
                log.info("Node {0} found in joinedNodes. Returning context {1}.".format(binascii.hexlify(dict['eui64']),
                                                                                        str(dict['context'])))
                return dict['context']

        # if eui-64 is not found, create a new tentative context but only add it to the list of joined nodes in the GET
        # handler of the join resource
        context = oscoap.SecurityContext(masterSecret=self.MASTERSECRET,
                                         senderID=u.buf2str(senderID),
                                         recipientID=u.buf2str(recipientID),
                                         aeadAlgorithm=oscoap.AES_CCM_16_64_128())

        log.info("Node {0} not found in joinedNodes. Instantiating new context based on the master secret.".format(
            binascii.hexlify(u.buf2str(eui64))))

        return context

# ======================== Interface with OpenVisualizer ======================================
class coapServer(eventBusClient.eventBusClient):
    # link-local prefix
    LINK_LOCAL_PREFIX = [0xfe, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    def __init__(self, coapResource, contextHandler):
        # log
        log.info("create instance")

        self.coapResource = coapResource

        # run CoAP server in testing mode
        # this mode does not open a real socket, rather uses PyDispatcher for sending/receiving messages
        # We interface this mode with OpenVisualizer to run JRC co-located with the DAG root
        self.coapServer = coap.coap(udpPort=d.DEFAULT_UDP_PORT, testing=True)
        self.coapServer.addResource(coapResource)
        self.coapServer.addSecurityContextHandler(contextHandler)
        self.coapServer.maxRetransmit = 1

        self.coapClient = None

        self.dagRootEui64 = None

        # store params

        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name='JRC',
            registrations=[
                {
                    'sender': self.WILDCARD,
                    'signal': 'getL2SecurityKey',
                    'callback': self._getL2SecurityKey_notif,
                },
                {
                    'sender': self.WILDCARD,
                    'signal': 'registerDagRoot',
                    'callback': self._registerDagRoot_notif
                },
                {
                    'sender': self.WILDCARD,
                    'signal': 'unregisterDagRoot',
                    'callback': self._unregisterDagRoot_notif
                },
            ]
        )

        # local variables
        self.stateLock = threading.Lock()

    # ======================== public ==========================================

    def close(self):
        # nothing to do
        pass

    # ======================== private =========================================

    # ==== handle EventBus notifications

    def _getL2SecurityKey_notif(self, sender, signal, data):
        '''
        Return L2 security key for the network.
        '''
        return {'index' : self.coapResource.networkKeyIndex, 'value' : self.coapResource.networkKey}

    def _registerDagRoot_notif(self, sender, signal, data):
        # register for the global address of the DAG root
        self.register(
            sender=self.WILDCARD,
            signal=(
                tuple(data['prefix'] + data['host']),
                self.PROTO_UDP,
                d.DEFAULT_UDP_PORT
            ),
            callback=self._receiveFromMesh,
        )

        # register to receive at link-local DAG root's address
        self.register(
            sender=self.WILDCARD,
            signal=(
                tuple(self.LINK_LOCAL_PREFIX + data['host']),
                self.PROTO_UDP,
                d.DEFAULT_UDP_PORT
            ),
            callback=self._receiveFromMesh,
        )

        self.dagRootEui64 = data['host']

    def _unregisterDagRoot_notif(self, sender, signal, data):
        # unregister global address
        self.unregister(
            sender=self.WILDCARD,
            signal=(
                tuple(data['prefix'] + data['host']),
                self.PROTO_UDP,
                d.DEFAULT_UDP_PORT
            ),
            callback=self._receiveFromMesh,
        )
        # unregister link-local address
        self.unregister(
            sender=self.WILDCARD,
            signal=(
                tuple(self.LINK_LOCAL_PREFIX + data['host']),
                self.PROTO_UDP,
                d.DEFAULT_UDP_PORT
            ),
            callback=self._receiveFromMesh,
        )

        self.dagRootEui64 = None

    def _receiveFromMesh(self, sender, signal, data):
        '''
        Receive packet from the mesh destined for JRC's CoAP server.
        Forwards the packet to the virtual CoAP server running in test mode (PyDispatcher).
        '''
        sender = openvisualizer.openvisualizer_utils.formatIPv6Addr(data[0])
        # FIXME pass source port within the signal and open coap client at this port
        self.coapClient = coap.coap(ipAddress=sender, udpPort=d.DEFAULT_UDP_PORT, testing=True, receiveCallback=self._receiveFromCoAP)
        self.coapClient.socketUdp.sendUdp(destIp='', destPort=d.DEFAULT_UDP_PORT, msg=data[1]) # low level forward of the CoAP message
        return True

    def _receiveFromCoAP(self, timestamp, sender, data):
        '''
        Receive CoAP response and forward it to the mesh network.
        Appends UDP and IPv6 headers to the CoAP message and forwards it on the Eventbus towards the mesh.
        '''
        self.coapClient.close()

        # UDP
        udplen = len(data) + 8

        udp = u.int2buf(self.coapClient.udpPort,2)  # src port
        udp += u.int2buf(sender[1],2) # dest port
        udp += [udplen >> 8, udplen & 0xff]  # length
        udp += [0x00, 0x00]  # checksum
        udp += data

        # destination address of the packet is CoAP client's IPv6 address (address of the mote)
        dstIpv6Address = u.ipv6AddrString2Bytes(self.coapClient.ipAddress)
        assert len(dstIpv6Address)==16
        # source address of the packet is DAG root's IPV6 address
        # use the same prefix (link-local or global) as in the destination address
        srcIpv6Address = dstIpv6Address[:8]
        srcIpv6Address += self.dagRootEui64
        assert len(srcIpv6Address)==16

        # CRC See https://tools.ietf.org/html/rfc2460.

        udp[6:8] = openvisualizer.openvisualizer_utils.calculatePseudoHeaderCRC(
            src=srcIpv6Address,
            dst=dstIpv6Address,
            length=[0x00, 0x00] + udp[4:6],
            nh=[0x00, 0x00, 0x00, 17], # UDP as next header
            payload=data,
        )

        # IPv6
        ip = [6 << 4]  # v6 + traffic class (upper nybble)
        ip += [0x00, 0x00, 0x00]  # traffic class (lower nibble) + flow label
        ip += udp[4:6]  # payload length
        ip += [17]  # next header (protocol); UDP=17
        ip += [64]  # hop limit (pick a safe value)
        ip += srcIpv6Address  # source
        ip += dstIpv6Address  # destination
        ip += udp

        # announce network prefix
        self.dispatch(
            signal        = 'v6ToMesh',
            data          = ip
        )

# ==================== Implementation of CoAP join resource =====================
class joinResource(coapResource.coapResource):
    def __init__(self):
        self.joinedNodes = []

        self.networkKey = u.str2buf(os.urandom(16)) # random key every time OpenVisualizer is initialized
        self.networkKeyIndex = [0x01] # L2 key index

        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'j',
        )

        self.addSecurityBinding((None, [d.METHOD_GET]))  # security context should be returned by the callback
    
    def GET(self,options=[]):
        respCode        = d.COAP_RC_2_05_CONTENT
        respOptions     = []

        k1 = {}
        k1[coseDefines.KEY_LABEL_KTY]   = coseDefines.KEY_VALUE_SYMMETRIC
        k1[coseDefines.KEY_LABEL_KID]   = u.buf2str(self.networkKeyIndex)
        k1[coseDefines.KEY_LABEL_K]     = u.buf2str(self.networkKey)

        join_response = [[k1]]
        join_response_serialized = cbor.dumps(join_response)

        respPayload     = [ord(b) for b in join_response_serialized]

        objectSecurity = oscoap.objectSecurityOptionLookUp(options)
        assert objectSecurity

        self.joinedNodes += [{'eui64' : u.buf2str(objectSecurity.kid[:8]), # remove last prepended byte
                        'context' : objectSecurity.context}]

        return (respCode,respOptions,respPayload)

if __name__ == "__main__":

    fileLogger = logging.handlers.RotatingFileHandler(
        filename    = 'test.log',
        mode        = 'w',
        backupCount = 5,
    )
    fileLogger.setFormatter(
        logging.Formatter(
            '%(asctime)s [%(name)s:%(levelname)s] %(message)s'
        )
    )

    consoleLogger = logging.StreamHandler()
    consoleLogger.setLevel(logging.DEBUG)

    for loggerName in [
            'coap',
            'coapOption',
            'coapUri',
            'coapTransmitter',
            'coapMessage',
            'socketUdpReal',
        ]:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(fileLogger)
        temp.addHandler(consoleLogger)
    
    log = logging.getLogger('JRC')
    log.setLevel(logging.DEBUG)
    log.addHandler(fileLogger)
    log.addHandler(consoleLogger)
 
    c = coap.coap()

    joinResource = joinResource()

    c.addResource(joinResource)

    c.addSecurityContextHandler(JRCSecurityContextLookup) # register callback


    raw_input('\n\nServer running. Press Enter to close.\n\n')
    
    c.close()

