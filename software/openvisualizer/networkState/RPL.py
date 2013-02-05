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
import random
from pprint import pprint

class RPL(object):
    '''
    classdocs
    '''
    
    _HEADER_LEN = 36 #DO len until transit information header
    _TRANSIT_INFORMATION_HEADER_LEN = 6
    _ADDR_LEN   = 8

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
        parents     = []
        destination = self._parseDestination(dao)
        source      = self._parseSource(dao) 
        #print ",".join(hex(c) for c in source)
        #check that the DAO has at least the minimum header

        
        if (len(dao) < self._HEADER_LEN):
             log.debug('received DAO with a too short header. src {0}, dest {1}, pkt {2}'.format(" ".join(hex(c) for c in source)," ".join(hex(c) for c in destination)," ".join(hex(c) for c in dao)))
             print 'received DAO with a too short header. src {0}, dest {1}, pkt {2}'.format(" ".join(hex(c) for c in source)," ".join(hex(c) for c in destination)," ".join(hex(c) for c in dao))
             return
        
        if (len(dao) < (self._HEADER_LEN + self._TRANSIT_INFORMATION_HEADER_LEN)):
             log.debug('received DAO without transit information header. This means that this node is reporting that has no parents or in its routing table there are no other nodes with a rank lower than its own. src {0}, dest {1}, pkt {2}'.format(" ".join(hex(c) for c in source)," ".join(hex(c) for c in destination)," ".join(hex(c) for c in dao)))
             print 'received DAO without transit information header. This means that this node is reporting that has no parents or in its routing table there are no other nodes with a rank lower than its own. src {0}, dest {1}, pkt {2}'.format(" ".join(hex(c) for c in source)," ".join(hex(c) for c in destination)," ".join(hex(c) for c in dao))
             return 
        
        if (len(source)!=self._ADDR_LEN):
             log.debug('received pkt with src address different than expected. src {0}, dest {1}, pkt {2}'.format(" ".join(hex(c) for c in source)," ".join(hex(c) for c in destination)," ".join(hex(c) for c in dao)))
             print 'received pkt with src address different than expected. src {0}, dest {1}, pkt {2}'.format(" ".join(hex(c) for c in source)," ".join(hex(c) for c in destination)," ".join(hex(c) for c in dao))
             return
          
        DAOheader   = self._retrieveDAOHeader(dao)
        parents     = self._parseParents(dao,DAOheader['Transit_information_length'])
        
        self.dataLock.acquire()
        #overwrites at every pkt. does not keep parents history.
        self.routes.update({str(source):parents})
        self.dataLock.release()
        #pprint(self.routes) 
    
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
    
  
    #======================== private =========================================
    
    def _getRouteTo_internal(self,destAddr,list):
        '''
        gets the route to the destiny recursive. 
        Elements in the resulting list are ordered from destiny to source
        '''
        
        if (destAddr is None):
          #no more parents.  
            return
        if (self.routes.get(str(destAddr)) is None):
            #this node does not have a list of parents. dagroot return.
            return
        else:
            #first time add destination address
            if (destAddr not in list):
                list.append(destAddr)
            
            # here pick a parent.
            parent=self.routes.get(str(destAddr))[0]
            
            #avoid loops
            if (parent not in list):
                list.append(parent)
                #add recursively non empty parents
                nextparent=self._getRouteTo_internal(parent,list)
                if (nextparent is not None):
                    list.append(nextparent)
    
    #Here the header + dao stuff
    #list: [120, 51, 58, 64, 155, 4, 128, 50, 136, 64, 0, 153,
    #2bytes IPHC, 6bytes ICMPv6 header including checksum, 1byte RPL instance iD== 136==0x88, 1byte flags, 1 byte reserved (0),1byte DAO sequence.  
    #DODAGID=16 BYTES = 32, 1, 17, 17, 34, 34, 51, 51, 20, 21, 146, 11, 3, 1, 0, 233, 
    #1byte options=6,
    #transit information type= 6, 
    #1 byte length options 1,
    #1byte flags= 0,
    #1 byte PAth control 64,
    #1 byte path sequence 6, 
    #1 byte path lifetime 170,
    # parents addresses 0, 0, 0, 0, 0, 0, 0, 233

    def _retrieveDAOHeader(self,dao):
        header={}
        header['IPHC_b0']=dao[0]
        header['IPHC_b1']=dao[1]
        #IPv6
        header['IPv6_nextHeader']=dao[2]
        header['IPv6_hoplimit']=dao[3]
        header['source_address'] = dao[4:12]
        
        header['ICMPv6_RPLType']=dao[12]
        header['ICMPv6_Code']=dao[13]
        header['ICMPv6_CheckSum_b0']=dao[14]
        header['ICMPv6_CheckSum_b1']=dao[15]
        #RPL
        header['RPL_InstanceID']=dao[16]
        header['RPL_flags']=dao[17]
        header['RPL_Reserved']=dao[18]
        header['RPL_DAO_Sequence']=dao[19]
        
        #DODAGID 16bytes
        header['DODAGID'] = dao[20:36]
                
        #transit information object
        header['Transit_information_type'] = dao[36]
        header['Transit_information_length'] = dao[37]
        header['Transit_information_flags'] = dao[38]
        header['Transit_information_path_control'] = dao[39]
        header['Transit_information_path_sequence'] = dao[40]
        header['Transit_information_path_lifetime'] = dao[41]
        #dao=dao[35:]
        for c in range(self._HEADER_LEN): dao.pop(0)
        
        for c in range(self._TRANSIT_INFORMATION_HEADER_LEN): dao.pop(0)
        return header
        
    
    ''' the DAO looks like this:
    0x78 0x33 0x3a IPHC header
    0x40 -- ?? -- maybe sender rank?? hop limit...
    I was expecting here instanceID (1B), IPv6 Next Header (1B),IPv6 Hop Limit (1B), IPv6 source address (8B),IPv6 dest address (8B)
    0x9b 0x4 0xeb 0x7a  ICMPv6 header (RPL type 9b,DAO, Checksum 2Bytes )
    0x88 0x40 0x0 0x99  ICMPv6 header (RPL instance,flags, reserved (0), DAO sequence)
    0x20 0x1 0x4 0x70 0x81 0xa 0xc0 0xf6 0x14 0x15 0x92 0x9 0x2 0x2c 0x0 0xa1 DODAGID 
    
    0x6 Option
    DAO transit INFO (type,EFLAGS,PathControl,PathSequence,pathlifetime
    0x6 0x1 0x0 0x40 0x16 0xaa 0x0 0x0 0x0 0x0 0x0 0x0 0x0 0xa1
    '''
                    
    def _parseSource(self,dao):
        #parse source from DAO.
        #[20, 21, 146, 11, 3, 1, 0, 233, 0, 0, 0, 0, 0, 0, 0, 225, 120, 51, 58, 64, 155, 4, 128, 50, 136, 64, 0, 153, 32, 1, 17, 17, 34, 
        #34, 51, 51, 20, 21, 146, 11, 3, 1, 0, 233, 6, 6, 1, 0, 64, 6, 170, 0, 0, 0, 0, 0, 0, 0, 233]
        res=dao[0:8] #source address starts at 0th byte in the packet.
        for c in range(8): dao.pop(0)
        #dao=dao[8:]#remove source from the chunk of bytes
        return res  
    
    def _parseDestination(self,dao):
        #parse dest from DAO.
        #[0, 0, 0, 0, 0, 0, 0, 225, 120, 51, 58, 64, 155, 4, 128, 50, 136, 64, 0, 153, 32, 1, 17, 17, 34, 
        #34, 51, 51, 20, 21, 146, 11, 3, 1, 0, 233, 6, 6, 1, 0, 64, 6, 170, 0, 0, 0, 0, 0, 0, 0, 233]
        res=dao[0:8] #dest address starts at 0th byte in the packet. because it has been cut by get source
        for c in range(8): dao.pop(0)
        return res  
    
    
    def _parseParents(self,dao,length):
        result=[]
        for i in range(length):
            result.append(dao[i*8:(i+1)*8])
        #parse all parents.
        return result
    
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
                    