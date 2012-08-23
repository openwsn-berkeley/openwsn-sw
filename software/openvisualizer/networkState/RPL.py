'''
Created on 17/08/2012

@author: xvilajosana
'''
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('RPL')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

class RPL(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        # local variables
        self.routes     = {} #empty dictionary
        self.dataLock   = threading.Lock()
     
    #======================== public ==========================================
        
    def update(self,dao):    
        '''
        updates the DAO table
        '''
        parents    = []
        source     = self._parseSource(dao) 
        parents    = self._parseParents(dao)
        
        self.dataLock.acquire()
        self.routes.update({source:parents})
        self.dataLock.release()
    
    def getRouteTo(self,destAddr):
        
        list = []
        
        try:
            self.dataLock.acquire()
            self._getRouteTo_internal(destAddr,list)
        except Exception as err:
            log.error(err)
            raise
        finally:
            self.dataLock.release()
        
        return list
    
    def _getRouteTo_internal(self,destAddr,list):
        '''
        gets the route to the destiny recursive. 
        Elements in the resulting list are ordered from destiny to source
        '''
        
        if (destAddr is None):
          #no more parents.  
            return
        if (self.routes.get(destAddr) is None):
            #this node does not have a list of parents. dagroot return.
            return
        else:
            #first time add destination address
            if (destAddr not in list):
                list.append(destAddr)
            
            # here pick a parent.
            parent=self.routes.get(destAddr)[0]
            
            #avoid loops
            if (parent not in list):
                list.append(parent)
                #add recursively non empty parents
                nextparent=self.getRouteTo(parent,list)
                if (nextparent is not None):
                    list.append(nextparent)
    
    #======================== private =========================================
    
    def _parseSource(self,dao):
        #parse source from DAO. 
        #dao=dao[8:10] #source address starts at 8th byte in the packet.
        return '1.1.1.' + str(random.randint(1,5))  #dummy
    
    def _parseParents(self,daos):
        parents=[]
        
        #parse all parents.
        
        #dummy
        return ['1.1.1.' + str(random.randint(1,5)),'1.1.1.' + str(random.randint(1,5)),'1.1.1.' + str(random.randint(1,5)),'1.1.1.' + str(random.randint(1,5))]
    
    #======================== helpers =========================================
    
    def test(self):
        import random
        for i in range(10):
            try:
               dao="1.1.1." + (str(i)) 
               self.update(dao)
            except Exception as err:
                print err
        
        print self.routes
        source='1.1.1.' + str(random.randint(1,5))
        print source
        print self.getRouteTo(source)
                    