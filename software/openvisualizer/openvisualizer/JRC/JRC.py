import threading
from   coap   import    coap,                    \
                        coapResource,            \
                        coapDefines as d,        \
                        coapOption as o,         \
                        coapUtils as u,          \
                        coapObjectSecurity as oscoap
import coseDefines
import logging.handlers
from openvisualizer.eventBus import eventBusClient

log = logging.getLogger('JRC')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import cbor
import binascii

MASTERSECRET = binascii.unhexlify('000102030405060708090A0B0C0D0E0F')
KEY_VALUE = [0xe6, 0xbf, 0x42, 0x87, 0xc2, 0xd7, 0x61, 0x8d, 0x6a, 0x96, 0x87, 0x44, 0x5f, 0xfd, 0x33, 0xe6]  # default L2 key for the network
KEY_ID = [0x01]  # L2 key index

# ======================== Context Handler needs to be registered =============================

def JRCSecurityContextLookup(kid):
    kidBuf = u.str2buf(kid)

    eui64 = kidBuf[:-1]
    senderID = eui64 + [0x01]  # sender ID of JRC is reversed
    recipientID = eui64 + [0x00]

    context = oscoap.SecurityContext(masterSecret=MASTERSECRET,
                                     senderID=u.buf2str(senderID),
                                     recipientID=u.buf2str(recipientID),
                                     aeadAlgorithm=oscoap.AES_CCM_16_64_128())

    return context

# ======================== Interface with OpenVisualizer ======================================
class JRC(eventBusClient.eventBusClient):

    def __init__(self):
        # log
        log.info("create instance")

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
        return {'index' : KEY_ID, 'value' : KEY_VALUE}

# ==================== Implementation of CoAP join resource =====================
class joinResource(coapResource.coapResource):
    
    def __init__(self):
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
        k1[coseDefines.KEY_LABEL_KID]   = u.buf2str(KEY_ID)
        k1[coseDefines.KEY_LABEL_K]     = u.buf2str(KEY_VALUE)

        join_response = [[k1]]
        join_response_serialized = cbor.dumps(join_response)

        respPayload     = [ord(b) for b in join_response_serialized]
        
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

