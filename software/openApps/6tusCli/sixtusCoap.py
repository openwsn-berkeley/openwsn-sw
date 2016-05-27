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
        target_addr=self._convertAddress2bytes(target_addr) 
        params += target_addr 
        params += [int(slot_type)]  
        params += [int(shared)] 
        #2bytes slotnum:
        slotnum=int(slot_num)
        byte1=(slotnum>>8)&0x00FF
        byte2= slotnum & 0x00FF
        params += [byte2]
        params += [byte1]
        params += [int(ch_offset)]
          
        log.debug('Following PUT command entered:'+ ",".join( str(c) for c in params))
        
        url='coap://[{0}]:{1}/{2}/'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE)
        try:
            self.coap.PUT(uri=url,payload=params)
        except Exception as err:
            log.error("Cannot access the resource {0}:{1}".format(url,err))
            print "Cannot access the resource {0}:{1}".format(url,err)
            
            
               
    def UPDATE_LINK(self,dst_url,target_addr,slot_num,slot_type,shared,ch_offset):
        params  = []
        params += [self.UPDATE_LINK_TYPE]
        params += [1] #one link
        target_addr=self._convertAddress2bytes(target_addr) 
        params += target_addr  
        params += [int(slot_type)]  
        params += [int(shared)] 
        #2bytes slotnum:
        slotnum=int(slot_num)
        byte1=(slotnum>>8)&0x00FF
        byte2= slotnum & 0x00FF
        params += [byte2]
        params += [byte1]
        params += [int(ch_offset)] 
        log.debug('Following UPDATE command entered:'+ ",".join( str(c) for c in params))
        
        url='coap://[{0}]:{1}/{2}/'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE)
        try:
            self.coap.PUT(uri=url,payload=params)
        except Exception as err:
            log.error("Cannot access the resource {0}:{1}".format(url,err))
            print "Cannot access the resource {0}:{1}".format(url,err)
            
    def READ_LINK(self,dst_url,target_addr,slot_num):
        target_addr=self._convertAddress2bytes(target_addr) 
        url='coap://[{0}]:{1}/{2}/{3}/{4}/{5}/{6}'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE,self.READ_LINK_TYPE,1,target_addr,slot_num)
        log.debug('Following GET command entered:'+ url)
        print url
        try:
           res=self.coap.GET(uri=url)
           return res
        except Exception as err:
            log.error("Cannot access the resource {0}:{1}".format(url,err))
            print "Cannot access the resource {0}:{1}".format(url,err)
            
    def DELETE_LINK(self,dst_url,target_addr,slot_num):
        params  = []
        params += [self.DELETE_LINK_TYPE]
        params += [1] #one link
        target_addr=self._convertAddress2bytes(target_addr) 
        params += target_addr
        #2bytes slotnum:
        slotnum=int(slot_num)
        byte1=(slotnum>>8)&0x00FF
        byte2= slotnum & 0x00FF
        params += [byte2]
        params += [byte1]  
        url='coap://[{0}]:{1}/{2}/'.format(dst_url,d.DEFAULT_UDP_PORT,self.RESOURCE)
        log.debug('Following DELETE command entered:'+ ",".join( str(c) for c in params))
        try:
           res=self.coap.DELETE(uri=url,payload=params)
        except Exception as err:
            log.error("Cannot access the resource {0}:{1}".format(url,err))
            print "Cannot access the resource {0}:{1}".format(url,err)
            
    def quit(self):
        raise NotImplementedError()
    
    
    
  
         
    #======================== public ==========================================
    
   
   
    
    #======================== private =========================================
    
    def hex2buf(self,s):
        '''
        \brief Convert a string of hex caracters into a byte list.
        
        That is: 'abcdef00' -> [0xab,0xcd,0xef,0x00]
        
        \param[in] s The string to convert
        
        \returns A list of integers, each element in [0x00..0xff].
        '''
        assert type(s)==str
        assert len(s)%2 == 0
    
        returnVal = []
    
        for i in range(len(s)/2):
            realIdx = i*2
            returnVal.append(int(s[realIdx:realIdx+2],16))
    
        return returnVal
    
    def _convertAddress2bytes(self,target_addr):
         #format target so i can travel in the payload
        try:
            target_addr=target_addr.split("::")[1]
        except:#if it does not have :: nothing happens
            pass 
        newstr = target_addr.replace(":", "")
        return self.hex2buf(newstr)
    