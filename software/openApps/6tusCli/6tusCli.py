


'''
Created on 02/05/2013

@author: xvilajosana
'''

import sys
import os
import threading

if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..','..','..','coap','coap')) # coap/
    sys.path.insert(0, os.path.join(cur_path, '..', '..','openvisualizer','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    
    
from coap import *

class SixTusCli(threading.Thread):
    
    CREATE_LINK = 0
    READ_LINK = 1
    UPDATE_LINK = 2
    DELETE_LINK = 3
    
    CELLTYPE_OFF = 0
    CELLTYPE_ADV = 1
    CELLTYPE_TX = 2
    CELLTYPE_RX = 3
    CELLTYPE_TXRX = 4
    CELLTYPE_SERIALRX = 5
    CELLTYPE_MORESERIALRX = 6
    
    
    def __init__(self):
        
         # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'SixTusCli'
        
        # store params
        self.src     = "BBBB::1"
        self.dst     = "coap://[BBBB::1415:923b:0301:00e9]/6tus"
        
        self.commandLock =threading.Lock()
        self.coap = coap(self.src) 
        
        self.goOn=True
         
    #======================== public ==========================================
    
    #======================== private =========================================
    def run(self):
       
        #create one element at a time by now.
        #0 1 1415:923b::009e 7 2 0 11 
       
        while self.goOn:
            data = []
            data +=[self.CREATE_LINK]
            data +=[1] #one element only by now
            
            # CLI stops here each time a user needs to call a command
            params = raw_input('> Introduce the target node for the link (e.g): 1415:923b:0000:009e ')
            #TODO this address needs to be formatted in the right way so the mote can read it, ideally should be an array of bytes
            data +=[params] 
            
            params = raw_input('> Introduce the time slot (e.g): 11 ')
            
            data +=[params] 
            
            params = raw_input('> Introduce the cell type (0-off,1-adv,2-tx,3-rx,4-txrx) ')
            
            data +=[params] 
            
            params = raw_input('> Introduce whether the link is shared or not (0-not-shared,1-shared) ')
            
            data +=[params] 
            
            params = raw_input('> Introduce the freq offset [0 to 16] ')
            
            data +=[params] 
            
            # log
            log.debug('Following command entered:'+ ",".join( str(c) for c in data))
            print 'Following command entered:'+ ",".join( str(c) for c in data)
             
            #TODO verify params
            
            #send the request
            self.coap.PUT(uri=self.dst,payload=params)
   
   
#this initializes everything
def main():
    
    cli = SixTusCli()
    cli.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('6tusCli.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['6tusCli',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()