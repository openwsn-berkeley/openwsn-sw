'''
\brief Module which receives DAO messages and calculates source routes.

\author Xavi Vilajosana <xvilajosana@eecs.berkeley.edu>, January 2013.
'''

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('RPL')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
from   openType import typeUtils as u

class RPL(object):
    
    def __init__(self):
        
        # local variables
        self.dataLock   = threading.Lock()
        self.parents    = {}
     
    #======================== public ==========================================
        
    def update(self,dao):    
        '''
        \brief Indicate a new DAO was received.
        
        This function parses the received packet, and if valid, updates the
        information needed to compute source routes.
        '''
        
        # retrieve source and destination
        try:
            destination      = dao[0:8]
            source           = dao[8:16]
            dao              = dao[16:]
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for destination and source".format(len(dao)))
            return
        
        # log
        output               = []
        output              += ['received DAO:']
        output              += ['- destination : {0}'.format(u.formatAddress(destination))]
        output              += ['- source :      {0}'.format(u.formatAddress(source))]
        output              += ['- dao :         {0}'.format(u.formatBuf(dao))]
        output               = '\n'.join(output)
        log.debug(output)
        
        # retrieve DAO header
        dao_header           = {}
        try:
            # IPHC header
            dao_header['IPHC_b0']                               = dao[0]
            dao_header['IPHC_b1']                               = dao[1]
            dao_header['IPv6_nextHeader']                       = dao[2]
            dao_header['IPv6_hoplimit']                         = dao[3]
            dao_header['source_address']                        = dao[4:12]
            # ICMPv6 header
            dao_header['ICMPv6_RPLType']                        = dao[12]
            dao_header['ICMPv6_Code']                           = dao[13]
            dao_header['ICMPv6_CheckSum_b0']                    = dao[14]
            dao_header['ICMPv6_CheckSum_b1']                    = dao[15]
            # RPL header
            dao_header['RPL_InstanceID']                        = dao[16]
            dao_header['RPL_flags']                             = dao[17]
            dao_header['RPL_Reserved']                          = dao[18]
            dao_header['RPL_DAO_Sequence']                      = dao[19]
            # DODAGID
            dao_header['DODAGID']                               = dao[20:36]
            # transit information option
            dao_header['Transit_information_type']              = dao[36]
            dao_header['Transit_information_length']            = dao[37]
            dao_header['Transit_information_flags']             = dao[38]
            dao_header['Transit_information_path_control']      = dao[39]
            dao_header['Transit_information_path_sequence']     = dao[40]
            dao_header['Transit_information_path_lifetime']     = dao[41]
            
            dao              = dao[42:]
        except IndexError:
            log.warning("DAO too short ({0} bytes), no space for DAO header".format(len(dao)))
            return
        
        # log
        log.debug('Transit_information_length={0}'.format(dao_header['Transit_information_length']))
        
        # retrieve parents
        parents              = []
        try:
            for i in range(dao_header['Transit_information_length']):
                parents     += [dao[i*8:(i+1)*8]]
        except IndexError:
            log.warning("could not retrieve parents from {0} bytes".format(len(dao)))
            return
        
        # log
        output               = []
        output              += ['parents:']
        for p in parents:
            output          += ['- {0}'.format(u.formatAddress(p))]
        output               = '\n'.join(output)
        log.debug(output)
        
        # if you get here, the DAO was parsed correctly
        
        # update parents information with parents collected
        with self.dataLock:
            self.parents.update({tuple(source):parents})
    
    def getRouteTo(self,destAddr):
        '''
        \brief Retrieve the source route to a given mote.
        
        \param[in] destAddr The EUI64 address of the final destination.
        
        \return The source route, a list of EUI64 address, order from
            destination to source.
        '''
        
        sourceRoute = []
        with self.dataLock:
            try:
                self._getRouteTo_internal(destAddr,sourceRoute)
            except Exception as err:
                log.error(err)
                raise
        
        return sourceRoute
    
    #======================== private =========================================
    
    def _getRouteTo_internal(self,destAddr,sourceRoute):
        
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
            nextparent       = self._getRouteTo_internal(parent,sourceRoute)
            
            if nextparent:
                sourceRoute += [nextparent]
    
    #======================== helpers =========================================
    