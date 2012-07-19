import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('InjectorUdp')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import socket

import Injector

class InjectorUdp(Injector.Injector):
    
    #======================== public ==========================================
    
    @classmethod
    def inject(self,destination=None,payload=None):
        
        # check that destination is well formatted
        assert len(destination)==2
        destIp   = destination[0]
        assert type(destIp)==str
        destPort = destination[1]
        assert type(destPort)==int
        
        # send payload over UDP socket
        sock = socket.socket(socket.AF_INET6,    # IPv6
                             socket.SOCK_DGRAM ) # UDP
        sock.sendto(''.join([chr(b) for b in payload]),
                    (destIp, destPort) )
    
    #======================== private =========================================