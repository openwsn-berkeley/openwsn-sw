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
from   epparser    import ParserOneNum
from   publisher   import PublisherScreen

UDP_PORT = 61000

class EpUdpRawCli(EndPointCli.EndPointCli):
    
    def __init__(self,endPoint):
        
        # initialize parent class
        EndPointCli.EndPointCli.__init__(self,endPoint,"endPoint UDP Raw")

def main():
    
    # create an endpoint
    endPoint  = EndPoint.EndPoint(
                        ListenerUdp.ListenerUdp(UDP_PORT),                     # listener
                        ParserOneNum.ParserOneNum(),                           # parser
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