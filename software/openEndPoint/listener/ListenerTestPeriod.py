import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ListenerTestPeriod')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import random

class ListenerTestPeriod(object):

    def __init__(self,period)
        
        # store params
        self.period     = period
        
        # initialize the parent class
        Listener.Listener.__init__(self)
        
    #======================== public ==========================================
    
    def getData(self):
        
        if not self.goOn:
            raise TearDownError()
        
        time.sleep(self.period)
        
        if not self.goOn:
            raise TearDownError()
        
        return (time.time,                                      # timestampe
                ('testHarness'),                                # source
                [random.randint(0,100) for b in range(10)])     # data
    
    def stop(self):
        # declare that this thread has to stop
        self.goOn = False
        
        # send some dummy value into the socket to trigger a read
        self.socket_handler.sendto( 'stop', ('::1',self.port) )
    
    #======================== private =========================================