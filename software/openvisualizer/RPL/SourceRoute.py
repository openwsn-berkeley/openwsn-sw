'''
\brief Module which receives DAO messages and calculates source routes.

\author Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>, January 2013.
\author Thomas Watteyne <watteyne@eecs.berkeley.edu>, April 2013.
'''

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SourceRoute')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
from   openType import typeUtils as u

class SourceRoute(object):
   
    _TARGET_INFORMATION_TYPE  = 0x05
    _TRANSIT_INFORMATION_TYPE = 0x06
    
    def __init__(self):
        
        # local variables
        self.dataLock        = threading.Lock()
        self.parents         = {}
    
    #======================== public ==========================================
        
    def indicateDAO(self,tup):    
        '''
        \brief Indicate a new DAO was received.
        
        This function parses the received packet, and if valid, updates the
        information needed to compute source routes.
        '''
        
        # retrieve source and destination
        try:
            source           = tup[0]
            if len(source)>8: 
                source=source[len(source)-8:]
            print source    
            dao              = tup[1]
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for destination and source".format(len(dao)))
            return
        
        # log
        output               = []
        output              += ['received DAO:']
        output              += ['- source :      {0}'.format(u.formatAddress(source))]
        output              += ['- dao :         {0}'.format(u.formatBuf(dao))]
        output               = '\n'.join(output)
        log.debug(output)
        
        # retrieve DAO header
        dao_header              = {}
        dao_transit_information = {}
        dao_target_information = {}
        
        try:
            # RPL header
            dao_header['RPL_InstanceID']                        = dao[0]
            dao_header['RPL_flags']                             = dao[1]
            dao_header['RPL_Reserved']                          = dao[2]
            dao_header['RPL_DAO_Sequence']                      = dao[3]
            # DODAGID
            dao_header['DODAGID']                               = dao[4:20]
           
            dao              = dao[20:]
            # retrieve transit information header and parents
            parents              = []
            children             = []
                          
            while (len(dao)>0):  
               if (dao[0]==self._TRANSIT_INFORMATION_TYPE): 
               # transit information option
                   dao_transit_information['Transit_information_type']              = dao[0]
                   dao_transit_information['Transit_information_length']            = dao[1]
                   dao_transit_information['Transit_information_flags']             = dao[2]
                   dao_transit_information['Transit_information_path_control']      = dao[3]
                   dao_transit_information['Transit_information_path_sequence']     = dao[4]
                   dao_transit_information['Transit_information_path_lifetime']     = dao[5]
                   parents += [dao[6:14]]#address of the parent.
                   dao=dao[14:]
               elif  (dao[0]==self._TARGET_INFORMATION_TYPE):
                   dao_target_information['Target_information_type']                = dao[0]
                   dao_target_information['Target_information_length']              = dao[1]
                   dao_target_information['Target_information_flags']               = dao[2]
                   dao_target_information['Target_information_prefix_length']       = dao[3]
                   children += [dao[4:12]]#address of the parent.
                   dao=dao[12:]
               else:
                   log.warning("DAO with wrong Option. Neither Transit nor Target. Option is ({0})".format(dao[0]))
                   return
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for DAO header".format(len(dao)))
            return
        
        # log
        output               = []
        output              += ['parents:']
        for p in parents:
            output          += ['- {0}'.format(u.formatAddress(p))]
        output               = '\n'.join(output)
        log.debug(output)
        print output
        
        output               = []
        output              += ['children:']
        for p in children:
            output          += ['- {0}'.format(u.formatAddress(p))]
        output               = '\n'.join(output)
        log.debug(output)
        
        
        
        # if you get here, the DAO was parsed correctly
        
        # update parents information with parents collected
        with self.dataLock:
            self.parents.update({tuple(source):parents})
    
    def getSourceRoute(self,destAddr):
        '''
        \brief Retrieve the source route to a given mote.
        
        \param[in] destAddr The EUI64 address of the final destination.
        
        \return The source route, a list of EUI64 address, ordered from
            destination to source.
        '''
        
        sourceRoute = []
        with self.dataLock:
            try:
                self._getSourceRoute_internal(destAddr,sourceRoute)
            except Exception as err:
                log.error(err)
                raise
        
        #return [[0xaa]*8,[0xbb]*8,[0xcc]*8,] # poipoipoipoi
        
        return sourceRoute
    
    #======================== private =========================================
    
    def _getSourceRoute_internal(self,destAddr,sourceRoute):
        
        if not destAddr:
            # no more parents
            return
        
        if not self.parents.get(tuple(destAddr)):
            # this node does not have a list of parents
            return
        
        # first time add destination address
        if destAddr not in sourceRoute:
            sourceRoute     += [destAddr]
        
        # pick a parent
        parent               = self.parents.get(tuple(destAddr))[0]
        
        # avoid loops
        if parent not in sourceRoute:
            sourceRoute     += [parent]
            
            # add non empty parents recursively
            nextparent       = self._getSourceRoute_internal(parent,sourceRoute)
            
            if nextparent:
                sourceRoute += [nextparent]
    
    #======================== helpers =========================================
    