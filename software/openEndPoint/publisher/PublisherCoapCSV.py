'''
Created on 16/07/2012

@author: xvilajosana
'''
import logging
from logging import FileHandler, StreamHandler
log = logging.getLogger('PublisherCoapCSV')
log.setLevel(logging.DEBUG)
log.addHandler(StreamHandler())

import time

import Publisher
  
PATH_FIELD = 1
PATH_SUBFIELD = 3

class PublisherCoapCSV(Publisher.Publisher):
    
    FORMAT_TIMESTAMP = '%Y/%m/%d %H:%M:%S'
  
    #======================== public ==========================================
    
    def publish(self,timestamp,source,data):
        #create logger according to app name.
        optionList=data['header'].getOptionList()
        app=optionList[PATH_FIELD]
        app=app[PATH_SUBFIELD]
        strname="".join(chr(b) for b in app)
        fh=FileHandler(strname +".csv", "a")
        fh.setLevel(logging.INFO)
        root=logging.getLogger(strname)
        root.setLevel(logging.INFO)
        try:
            root.removeHandler(fx)
        except:
            pass
        root.addHandler(fh)#add the handler to the logger
        
        root.info("{0},{1}".format(self._formatTimestamp(timestamp),data["parsed"]))
        log.debug("{0},{1}".format(self._formatTimestamp(timestamp),data["parsed"]))
    
    #======================== private =========================================
    
    def _formatTimestamp(self,timestamp):
        return time.strftime(self.FORMAT_TIMESTAMP,time.localtime(timestamp))
