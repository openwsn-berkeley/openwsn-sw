import os
import sys
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openCli'))    # openCli/
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openEndPoint/
    
import logging
import logging.handlers

from   engine      import EndPointCli
from   engine      import EndPoint
from   listener    import ListenerUdp
from   epparser    import ParserOneList
from   publisher   import PublisherScreen
from   injector    import InjectorCoap, InjectorCoapLed

UDP_PORT = 5683

class EpUdpRawCli(EndPointCli.EndPointCli):
    
    def __init__(self,endPoint):
        
        # initialize parent class
        EndPointCli.EndPointCli.__init__(self,endPoint,"endPoint UDP Raw")
    
        # add commands
        self.registerCommand('inject',
                             'in',
                             'inject data to CoAP resource',
                             [],
                             self._handlerInject)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def _handlerInject(self,params):
        destination_ip       = "2001:470:810a:d42f:1415:9209:22c:99"
        destination_port     = 5683
        destination_resource = 'l'
        payload              = [0x01,0x02]
        InjectorCoap.InjectorCoap.inject((destination_ip,destination_port),
                                         destination_resource,
                                         payload)

def main():
    
    # create an endpoint
    endPoint  = EndPoint.EndPoint(
                        ListenerUdp.ListenerUdp(UDP_PORT),                     # listener
                        ParserOneList.ParserOneList(),                         # parser
                        [                                                      # publishers
                            PublisherScreen.PublisherScreen(),
                        ],
                    )
    endPoint.start()
    
    # create an openCLI
    cli = EpUdpRawCli(endPoint)
    cli.start()
    
if __name__=='__main__':
    
    # setup loggin
    logHandler = logging.handlers.RotatingFileHandler('EpUdpRawCli.log',
                                                      maxBytes=2000000,
                                                      backupCount=5,
                                                      mode='w')
    logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
    for loggerName in ['EndPoint',
                       'ListeningEngine',
                       'ListenerUdp',
                       'ProcessingEngine',
                       'ParserOneNum',
                       'PublishingEngine',
                       'PublisherScreen',
                      ]:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(logHandler)

    # start the application
    main()