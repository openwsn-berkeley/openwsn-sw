import os
import sys
import threading
from   coap   import    coap,                    \
                        coapResource,            \
                        coapDefines as d,        \
                        coapOption as o
import coseDefines
import logging
import logging.handlers
log = logging.getLogger('JRC')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import cbor


class JRC():

    def __init__(self):
        # log
        log.info("create instance")

        # open coap server
        self.c = coap.coap()

        # install resource
        self.c.addResource(joinResource())

    def close(self):
        self.c.close()

class joinResource(coapResource.coapResource):

    KEY_VALUE = 'e6bf4287c2d7618d6a9687445ffd33e6'.decode('hex') # default L2 key for the network
    KEY_ID    = '01'.decode('hex') # key identifier
    
    def __init__(self):
        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'j',
        )
    
    def GET(self,options=[]):
        
        respCode        = d.COAP_RC_2_05_CONTENT
        respOptions     = [o.ContentFormat([d.FORMAT_CBOR])]

        k1 = {}
        k1[coseDefines.KEY_LABEL_KTY]   = coseDefines.KEY_VALUE_SYMMETRIC
        k1[coseDefines.KEY_LABEL_KID]   = self.KEY_ID
        k1[coseDefines.KEY_LABEL_K]     = self.KEY_VALUE

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
 
    jrc = JRC()

    raw_input('\n\nServer running. Press Enter to close.\n\n')
    jrc.close()

