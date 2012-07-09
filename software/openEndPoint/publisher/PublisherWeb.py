import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublisherWeb')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import web
import json

import Publisher

webDataSource = None

class dataResource(object):
    def GET(self):
        global webDataSource
        
        #web.header('Content-Type', 'text/json')
        return webDataSource.getData()

class index(object):
    def GET(self):
        return "Hello, World!"

class OpenWebApp(web.application):
    
    urls = (
        '/',      'index',
        '/data/', 'dataResource',
    )
    
    def __init__(self, dataSource):
        global webDataSource
        
        webDataSource = dataSource
        
        # initialize parent class
        web.application.__init__(self,self.urls,globals())

class OpenWebAppThread(threading.Thread):
    
    def __init__(self, dataSource):
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name       = "OpenWebAppThread"
        
        # local variables
        self.openWebApp = OpenWebApp(dataSource)
    
    def run(self):
        self.openWebApp.run()
        
class DataQueue(object):

    QUEUE_SIZE = 100
 
    def __init__(self):
        self.dataLock = threading.Lock()
        self.data     = []
    
    #======================== public ==========================================
    
    def push(self,timestamp,data):
        self.dataLock.acquire()
        self.data.append(data)
        if len(self.data)>self.QUEUE_SIZE:
            self.data.pop(0)
        self.dataLock.release()
        
    def getData(self):
        self.dataLock.acquire()
        returnVal = json.dumps(self.data,sort_keys=True,indent=4)
        self.dataLock.release()
        
        return returnVal

class PublisherWeb(Publisher.Publisher):
    
    def __init__(self):
        global webDataSource
        
        # store params
        
        # log
        log.debug("creating instance")
        
        # initialize parent class
        Publisher.Publisher.__init__(self)
        
        # global variables
        webDataSource  = self
        
        # local variables
        self.dataQueue = DataQueue()
        self.webApp    = OpenWebAppThread(self)
    
    def run(self):
        self.webApp.start()
    
    #======================== public ==========================================
    
    def publish(self,timestamp,source,data):
        
        # log
        log.debug("{2} from {1} at {0}".format(timestamp,
                                               source,
                                               data))
        
        print data
        
        # add to data
        self.dataQueue.push(timestamp,data)
        
    def getData(self):
        return self.dataQueue.getData()
    
    #======================== private =========================================
    