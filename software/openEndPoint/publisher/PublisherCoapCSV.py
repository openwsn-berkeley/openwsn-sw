'''
Created on 16/07/2012

@author: xvilajosana
'''
import logging
import inspect
import os

from logging import FileHandler, StreamHandler
from test.test_binop import isint
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
        
        #convert : to _ because windows do not like folders with :
        s=source[0].replace(':','_')
        
        #create logger according to app name.
        
        optionList=data['header'].getOptionList()
        app=optionList[PATH_FIELD]
        app=app[PATH_SUBFIELD]
        strname="".join(chr(b) for b in app)
        #check if there is an instance of that file handler
        root=logging.getLogger(s+strname)
        root.setLevel(logging.INFO)
        
        
        print " ".join(h.get_name() for h in root.handlers)
        
        for h in root.handlers:
            if isinstance(h, FileHandler):
                name=h.get_name()
                if name in (s+strname):#already exists
                    pass
                else:#create the new filehandler
                    if not os.path.exists(os.path.curdir +"/"+ s):
                        os.makedirs(os.path.curdir +"/" + s)
                    fh=FileHandler(os.path.curdir +"/"+ s +"/" +strname +".csv", "a")
                    #fh=FileHandler(strname +".csv", "a")
                    fh.set_name(s+strname)#set a name to be able to find it 
                    fh.setLevel(logging.INFO)
                    root.addHandler(fh)#add the handler to the logger only once
            else:#other handlers 
                 pass
                    
        #the first time will be added here
        if len(root.handlers)==0:
            
            if not os.path.exists(os.path.curdir +"/"+ s):
                os.makedirs(os.path.curdir +"/" + s)    
            fh=FileHandler(os.path.curdir +"/"+ s +"/" + strname +".csv", "a")
            fh.setLevel(logging.INFO)
            fh.set_name(s+strname)#set a name to be able to find it 
            root.addHandler(fh)#add the handler to the logger only once
        
        #prepare the ; separated tuples to be printed in csv
        x=";".join(",".join(str(val) for val in dict.itervalues() ) for dict in data["parsed"])
        
        root.info("{0},{1}".format(self._formatTimestamp(timestamp),x))
        log.debug("{0},{1}".format(self._formatTimestamp(timestamp),x))
    
    #======================== private =========================================
    
    def _formatTimestamp(self,timestamp):
        return time.strftime(self.FORMAT_TIMESTAMP,time.localtime(timestamp))
