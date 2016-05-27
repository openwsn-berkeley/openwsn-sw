import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ListenerUdp')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import socket
import time

import Listener

class ListenerUdp(Listener.Listener):

    BUFSIZE = 1024
    
    def __init__(self,port):
        # log
        log.debug('creating instance')
        
        # store params
        self.port       = port
        
        # initialize the parent class
        Listener.Listener.__init__(self)
        
        # open UDP port
        try:
            self.socket_handler  = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            self.socket_handler.bind(('',self.port))
        except socket.error as err:
            log.critical(err)
            raise
    
    #======================== public ==========================================
    
    def getData(self):
        try:
            # blocking wait for something from UDP socket
            raw,conn = self.socket_handler.recvfrom(self.BUFSIZE)
        except socket.error as err:
            log.critical("socket error: {0}".format(err))
            raise
        else:
            if not raw:
                log.error("no data read from socket")
                return
            if not self.goOn:
                log.warning("goOn is false; tearing down")
                raise TearDownError()
            
            timestamp = time.time()
            source    = (conn[0],conn[1])
            data      = [ord(b) for b in raw]
            
            log.debug("got {2} from {1} at {0}".format(timestamp,source,data))
            
            return timestamp, source, data
    
    def stop(self):
        # declare that this thread has to stop
        self.goOn = False
        
        # send some dummy value into the socket to trigger a read
        self.socket_handler.sendto( 'stop', ('::1',self.port) )
    
    #======================== private =========================================