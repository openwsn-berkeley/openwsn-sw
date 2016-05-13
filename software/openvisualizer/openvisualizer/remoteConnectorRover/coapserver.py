import os
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here,'..'))
import glob
import json
import logging
log = logging.getLogger('coapServer')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

from   coap   import    coap,                    \
                        coapResource,            \
                        coapDefines as d


class pcInfo(coapResource.coapResource):

    def __init__(self, app):
        # initialize parent class
        self.app = app
        coapResource.coapResource.__init__(
            self,
            path = 'pcinfo',
        )

    def GET(self,options=[]):

        log.info('GET received')

        respCode        = d.COAP_RC_2_05_CONTENT
        respOptions     = []
        respPayload     = [ord(b) for b in self.listmotes()]

        return (respCode,respOptions,respPayload)

    def PUT(self,options=[],payload=None):

        asciipayload = ''.join([chr(i) for i in payload])

        log.info('PUT RECEIVED, payload :' + asciipayload)

        respCode = d.COAP_RC_2_05_CONTENT
        respOptions = []
        respPayload = [ord(b) for b in self.listmotes()]

        try :
            PCip = asciipayload.split(';')[0]
            PCport = asciipayload.split(';')[1]
            roverID = asciipayload.split(';')[2]
            self.app.startRemoteConnector(PCip, PCport, roverID)
        except :
            log.warning("Unexpected error:", sys.exc_info()[0])
            pass

        return (respCode, respOptions, respPayload)


    def listmotes(self):
        serialList = glob.glob('/dev/ttyUSB*')   # Get all Serial ports
        serialList += glob.glob('/dev/ttyAMA*')
        return json.dumps([serial for serial in serialList])
    