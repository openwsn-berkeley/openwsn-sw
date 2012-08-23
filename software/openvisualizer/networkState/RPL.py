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

#
import random

class RPL(object):
    '''
    classdocs
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        self.routes={} #empty dictionary.    
        
        
    def update(self,dao):    
        '''
        updates the DAO table
        '''
        parents=[]
        source = self.parseSource(dao) 
        parents = self.parseParents(dao)
        self.routes.update({source:parents})
        
    def parseParents(self,daos):
        parents=[]
        
        #parse all parents.
        
        #dummy
        return ['1.1.1.' + str(random.randint(1,5)),'1.1.1.' + str(random.randint(1,5)),'1.1.1.' + str(random.randint(1,5)),'1.1.1.' + str(random.randint(1,5))]
        
    
    def parseSource(self,dao):
        #parse source from DAO. 
        #dao=dao[8:10] #source address starts at 8th byte in the packet.
        return '1.1.1.' + str(random.randint(1,5))  #dummy
    
    def getRouteTo(self,destAddr,list):
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
        
    
    def test(self):
        for i in range(10):
            try:
               dao="1.1.1." + (str(i)) 
               self.update(dao)
            except Exception as err:
                print err
        
        print self.routes
        source='1.1.1.' + str(random.randint(1,5))
        print source
        route=[]
        self.getRouteTo(source,route)
        print route
                    