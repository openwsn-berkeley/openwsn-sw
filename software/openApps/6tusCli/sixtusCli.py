


'''
Created on 02/05/2013

@author: xvilajosana
'''
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('sixtusCli')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())


import sys
import os
import threading

if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..','..','..','coap','coap')) # coap/
    sys.path.insert(0, os.path.join(cur_path, '..', '..','openvisualizer','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', 'openCli'))  # openCli/
    
    
from OpenCli import OpenCli

from sixtusCoap import sixtusCoap

class sixtusCli(OpenCli):
       
    
    def __init__(self):
        
         # initialize parent class
        OpenCli.__init__(self,"6tus client",self.quit_cb)
        
        self.sixtusCoap = sixtusCoap() 
        # add commands
        # 1415:923b::009e 7 2 0 11 
        self.registerCommand('create_link',
                             'c',
                             'create a link',
                             ['dst_url','target_addr','slot_num','slot_type','shared','ch_offset'],
                             self._handlerCreateLink)

        self.registerCommand('update_link',
                             'u',
                             'updates a link',
                             ['dst_url','target_addr','slot_num','slot_type','shared','ch_offset'],
                             self._handlerUpdateLink)

        # add commands
        self.registerCommand('read_link',
                             'r',
                             'reads a link from the schedule',
                             ['dst_url','target_addr','slot_num',],
                             self._handlerReadLink)
         # add commands
        self.registerCommand('delete_link',
                             'd',
                             'deletes a link from the schedule',
                             ['dst_url','target_addr','slot_num',],
                             self._handlerDeleteLink)

        
    
    #example query from terminal: c BBBB::1415:920b:0301:00f2  BBBB::1415:920b:0301:00e9  7 2 0 11     
    def _handlerCreateLink(self,params):
        print 'CREATE_LINK: ' + ' '.join(params)
        log.debug('CREATE_LINK: ' + ' '.join(params))
        self.sixtusCoap.CREATE_LINK(params[0],params[1],params[2],params[3],params[4],params[5])
        
    def _handlerUpdateLink(self,params):
        print 'UPDATE_LINK: ' + ' '.join(params)
        log.debug('UPDATE_LINK: ' + ' '.join(params))
        self.sixtusCoap.UPDATE_LINK(params[0],params[1],params[2],params[3],params[4],params[5])    
   
    #the url will look like coap://[2001:0470:48b8:aaaa:1415:920b:0301:00e9]:5683/6tus/1/1/1415923b0000009e/3
    #the command to issue: r BBBB::1415:923b:0301:00e9 1415:923b::009e 7   
    def _handlerReadLink(self,params):
        print 'READ_LINK: ' + ' '.join(params)
        log.debug('READ_LINK: ' + ' '.join(params))
        self.sixtusCoap.READ_LINK(params[0],params[1],params[2])
        
        
    def _handlerDeleteLink(self,params):
        print 'DELETE_LINK: ' + ' '.join(params)
        log.debug('DELETE_LINK: ' + ' '.join(params))
        self.sixtusCoap.DELETE_LINK(params[0],params[1],params[2])    
    #===== helpers
    
    def quit_cb(self):
        print "quit"
        
#this initializes everything
def main():
    
    cli = sixtusCli()
    cli.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('sixtusCli.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['sixtusCli','sixtusCoap']:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()