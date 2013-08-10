'''
\brief Module which receives DAO messages and calculates source routes.

\author Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>, January 2013.
\author Thomas Watteyne <watteyne@eecs.berkeley.edu>, April 2013.
'''

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('topology')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

import openvisualizer_utils as u
from eventBus import eventBusClient

class topology(eventBusClient.eventBusClient):
    
    def __init__(self):
        
        # local variables
        self.dataLock        = threading.Lock()
        self.parents         = {}
        
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'topology',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'updateParents',
                    'callback'    : self.updateParents,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'getParents',
                    'callback'    : self.getParents,
                },
            ]
        )
    
    #======================== public ==========================================
    
    def getParents(self,sender,signal,data):
        return self.parents
    
    def updateParents(self,sender,signal,data):
        ''' inserts parent information into the parents dictionary '''
        with self.dataLock:
            #data[0] == source address, data[1] == list of parents
            self.parents.update({data[0]:data[1]})
    
    #======================== private =========================================
    
    #======================== helpers =========================================
