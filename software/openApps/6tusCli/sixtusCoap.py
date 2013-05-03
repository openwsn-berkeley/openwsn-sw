'''
Created on 03/05/2013

@author: xvilajosana
'''

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('sixtusCoap')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())


from coap    import *
import coapDefines as d

class sixtusCoap(object):
    
    CREATE_LINK_TYPE = 0
    READ_LINK_TYPE = 1
    UPDATE_LINK_TYPE = 2
    DELETE_LINK_TYPE = 3
    
    CELLTYPE_OFF = 0
    CELLTYPE_ADV = 1
    CELLTYPE_TX = 2
    CELLTYPE_RX = 3
    CELLTYPE_TXRX = 4
    CELLTYPE_SERIALRX = 5
    CELLTYPE_MORESERIALRX = 6
    RESOURCE = "6tus"
    
    def __init__(self):
        #get my address from interface??
        self.src     = "BBBB::1"
        #self.dst     = "coap://[BBBB::1415:923b:0301:00e9]/6tus" 
        self.coap = coap(self.src) 
        # store params
        
    #======================== public ==========================================
    
    def CREATE_LINK(self,dst_url,target_addr,slot_num,slot_type,shared,ch_offset):
        params  = []
        params += [self.CREATE_LINK_TYPE]
        params += [1] #one link
        params += [target_addr] 
        params += [slot_num]
        params += [slot_type]  
        params += [shared] 
        params += [ch_offset]  
        log.debug('Following PUT command entered:'+ ",".join( str(c) for c in params))
        
        url='coap://[{0}]:{1}/{2}/'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE)
        
        self.coap.PUT(uri=url,payload=params)
        
    def UPDATE_LINK(self,dst_url,target_addr,slot_num,slot_type,shared,ch_offset):
        params  = []
        params += [self.UPDATE_LINK_TYPE]
        params += [1] #one link
        params += [target_addr] 
        params += [slot_num]
        params += [slot_type]  
        params += [shared] 
        params += [ch_offset]  
        log.debug('Following UPDATE command entered:'+ ",".join( str(c) for c in params))
        
        url='coap://[{0}]:{1}/{2}/'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE)
        self.coap.PUT(uri=url,payload=params)
       
    def READ_LINK(self,dst_url,target_addr,slot_num):
        url='coap://[{0}]:{1}/{2}/{3}/{4}/{5}/{6}'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE,self.READ_LINK_TYPE,1,target_addr,slot_num)
        log.debug('Following GET command entered:'+ url)
        print url
        res=self.coap.GET(uri=url)
        return res
    
    def DELETE_LINK(self,dst_url,target_addr,slot_num):
        params  = []
        params += [self.DELETE_LINK_TYPE]
        params += [1] #one link
        params += [target_addr] 
        params += [slot_num]
        url='coap://[{0}]:{1}/{2}/'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE)
        log.debug('Following DELETE command entered:'+ ",".join( str(c) for c in params))
        res=self.coap.DELETE(uri=url,payload=params)
        
   
    def quit(self):
        raise NotImplementedError()
    
    
    
  
         
    #======================== public ==========================================
    
   
   
    
    #======================== private =========================================