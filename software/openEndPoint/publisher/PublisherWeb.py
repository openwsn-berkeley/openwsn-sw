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
import random

import Publisher

webDataSource = None
webTemplate   = None

class index(object):
    def GET(self):
        global webTemplate
        #raise web.seeother('/static/index.html')
        return webTemplate.googlegauge()
class allData(object):
    def GET(self):
        global webDataSource
        web.header('Content-Type', 'text/json')
        return webDataSource.getAllData()
class lastData(object):
    def GET(self):
        global webDataSource
        web.header('Content-Type', 'text/json')
        return webDataSource.getLastData()

class OpenWebApp(web.application):
    
    urls = (
        '/',     'index',
        '/all',  'allData',
        '/last', 'lastData',
    )
    
    def __init__(self, dataSource):
        global webDataSource
        global webTemplate
        
        webDataSource = dataSource
        webTemplate   = web.template.render('templates/')
        
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
        # start web app
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
        
    def getAllData(self):
        self.dataLock.acquire()
        returnVal = json.dumps(self.data,sort_keys=True,indent=4)
        self.dataLock.release()
        return returnVal
    
    def getLastData(self):
        
        self.dataLock.acquire()
        if self.data:
            lastVal = self.data[-1]['value']
        else:
            lastVal = 0
        self.dataLock.release()
        
        data = {
            'cols': [{'id': 'label', 'label': 'Label', 'type': 'string'},
                     {'id': 'value', 'label': 'Value', 'type': 'number'}],
            'rows': [{'c':[{'v': ''}, {'v': lastVal}]},],
        }
        returnVal = json.dumps(data)
        
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
        
        # add to data
        self.dataQueue.push(timestamp,data)
        
    def getAllData(self):
        return self.dataQueue.getAllData()
    
    def getLastData(self):
        return self.dataQueue.getLastData()
    
    #======================== private =========================================
    