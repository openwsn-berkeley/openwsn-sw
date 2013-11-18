import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('endPointTestCli')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import pprint

import OpenCli

class EndPointCli(OpenCli.OpenCli):

    def __init__(self,endPoint,appName):
        
        # store params
        self.endPoint = endPoint
        
        # initialize parent class
        OpenCli.OpenCli.__init__(self,appName,self.quit_cb)
        
        # add commands
        self.registerCommand('stats',
                             'st',
                             'list stats',
                             [],
                             self._handlerStats)
    
    #======================== public ==========================================
    
    def quit_cb(self):
        self.endPoint.stop()
    
    #======================== private =========================================
    
    def _handlerStats(self,params):
        pp = pprint.PrettyPrinter(indent=3)
        pp.pprint(self.endPoint.getStats())
