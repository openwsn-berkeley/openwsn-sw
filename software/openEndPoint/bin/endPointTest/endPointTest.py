import os
import sys
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openCli'))    # openCli/
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openEndPoint/
    
import logging
import logging.handlers

import OpenCli
from   engine      import EndPoint
from   listener    import ListenerTestPeriod
from   epparser    import ParserOneNum
from   publisher   import PublisherScreen

PERIOD_MS = 1000

class endPointTestCli(OpenCli.OpenCli):

    def __init__(self,endPoint):
        
        # store params
        self.endPoint     = endPoint
        
        # initialize parent class
        OpenCli.OpenCli.__init__(self,"endPoint test",self.quit_cb)
    
    def quit_cb(self):
        self.endPoint.stop()

def main():
    
    # create an endpoint
    endPoint  = EndPoint.EndPoint(
                        ListenerTestPeriod.ListenerTestPeriod(PERIOD_MS),      # listener
                        ParserOneNum.ParserOneNum(),                           # parser
                        [                                                      # publishers
                            PublisherScreen.PublisherScreen(),
                        ],
                    )
    endPoint.start()
    
    # create an openCLI
    cli = endPointTestCli(endPoint)
    cli.start()
    
if __name__=='__main__':
    
    # setup loggin
    logHandler = logging.handlers.RotatingFileHandler('endPointTest.log',
                                                      maxBytes=2000000,
                                                      backupCount=5,
                                                      mode='w')
    logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
    for loggerName in ['EndPoint',
                       'ListeningEngine',
                       'ListenerTestPeriod',
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