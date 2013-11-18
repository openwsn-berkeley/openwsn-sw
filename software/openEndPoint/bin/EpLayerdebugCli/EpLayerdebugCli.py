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
#from   epparser    import ParserOneNum
from   epparser    import ParserCoap
from   epparser    import ParserPayload
from   publisher   import PublisherScreen,PublisherCoapCSV

UDP_PORT = 5683

class EpLayerdebugCli(EndPointCli.EndPointCli):
    
    def __init__(self,endPoint):
        
        # initialize parent class
        EndPointCli.EndPointCli.__init__(self,endPoint,"endPoint Layerdebug")

def main():
    
    # create an endpoint
    endPoint  = EndPoint.EndPoint(
                        ListenerUdp.ListenerUdp(UDP_PORT),                     # listener
                        ParserPayload.ParserPayload(),                           # parser
                        [                                                      # publishers
                            #PublisherScreen.PublisherScreen(),
                            PublisherCoapCSV.PublisherCoapCSV()
                        ],
                    )
    endPoint.start()
    
    # create an openCLI
    cli = EpLayerdebugCli(endPoint)
    cli.start()
    
if __name__=='__main__':
    
    # setup loggin
    logHandler = logging.handlers.RotatingFileHandler('EpLayerdebugCli.log',
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
