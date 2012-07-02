
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteState')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import copy
import time
import threading
import pprint

from moteConnector import ParserStatus
from moteConnector import MoteConnectorConsumer

class StateElem(object):
    
    def __init__(self):
        self.meta                      = {}
        self.data                      = {}
        
        self.meta['numUpdates']        = 0
    
    def update(self):
        self.meta['lastUpdated']       = time.time()
        self.meta['numUpdates']       += 1
    
    def getData(self):
        
        returnVal = {}
        returnVal['meta'] = copy.deepcopy(self.meta)
        returnVal['data'] = {}
        for k,v in self.data.items():
            if isinstance(v,(list, tuple)):
                returnVal['data'][k] = [m.getData() for m in v]
            else:
                returnVal['data'][k] = v
        
        return returnVal
    
    def __str__(self):
        pp = pprint.PrettyPrinter(indent=3)
        return pp.pformat(self.getData())

class StateOutputBuffer(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['index_write']       = notif.index_write
        self.data['index_read']        = notif.index_read

class StateAsn(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['asn']               = notif.asn_0_1<<12 + \
                                         notif.asn_2_3<<4  + \
                                         notif.asn_4

class StateMacStats(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['syncCounter']       = notif.syncCounter
        self.data['minCorrection']     = notif.minCorrection
        self.data['maxCorrection']     = notif.maxCorrection
        self.data['numDeSync']         = notif.numDeSync

class StateScheduleRow(StateElem):

    def update(self,notif):
        StateElem.update(self)
        self.data['slotOffset']        = notif.slotOffset
        self.data['type']              = notif.type
        self.data['shared']            = notif.shared
        self.data['channelOffset']     = notif.channelOffset
        self.data['addrType']          = notif.addrType
        self.data['neighbor']          = notif.neighbor
        self.data['backoffExponent']   = notif.backoffExponent
        self.data['backoff']           = notif.backoff
        self.data['numRx']             = notif.numRx
        self.data['numTx']             = notif.numTx
        self.data['numTxACK']          = notif.numTxACK
        self.data['lastUsedAsn']       = notif.lastUsedAsn_0_1<<12 + \
                                         notif.lastUsedAsn_2_3<<4  + \
                                         notif.lastUsedAsn_4

class StateQueueRow(StateElem):
    
    def update(self,creator,owner):
        StateElem.update(self)
        self.data['creator']           = creator
        self.data['owner']             = owner

class StateQueue(StateElem):
    
    def __init__(self):
        StateElem.__init__(self)
        
        self.data['table'] = []
        for i in range(10):
            self.data['table'].append(StateQueueRow())
    
    def update(self,notif):
        StateElem.update(self)
        self.data['table'][0].update(notif.creator_0,notif.owner_0)
        self.data['table'][1].update(notif.creator_1,notif.owner_1)
        self.data['table'][2].update(notif.creator_2,notif.owner_2)
        self.data['table'][3].update(notif.creator_3,notif.owner_3)
        self.data['table'][4].update(notif.creator_4,notif.owner_4)
        self.data['table'][5].update(notif.creator_5,notif.owner_5)
        self.data['table'][6].update(notif.creator_6,notif.owner_6)
        self.data['table'][7].update(notif.creator_7,notif.owner_7)
        self.data['table'][8].update(notif.creator_8,notif.owner_8)
        self.data['table'][9].update(notif.creator_9,notif.owner_9)

class StateNeighborsRow(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['used']                   = notif.used
        self.data['parentPreference']       = notif.parentPreference
        self.data['stableNeighbor']         = notif.stableNeighbor
        self.data['switchStabilityCounter'] = notif.switchStabilityCounter
        self.data['addr_64b']               = notif.addr_64b
        self.data['DAGrank']                = notif.DAGrank
        self.data['numRx']                  = notif.numRx
        self.data['numTx']                  = notif.numTx
        self.data['numTxACK']               = notif.numTxACK
        self.data['asn']                    = notif.asn_0_1<<12 + \
                                              notif.asn_2_3<<4  + \
                                              notif.asn_4

class StateIsSync(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['isSync']            = notif.isSync

class StateIdManager(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['isDAGroot']         = notif.isDAGroot
        self.data['isBridge']          = notif.isBridge
        self.data['my16bID']           = notif.my16bID
        self.data['my64bID']           = notif.my64bID
        self.data['myPANID']           = notif.myPANID
        self.data['myPrefix']          = notif.myPrefix

class StateMyDagRank(StateElem):
    
    def update(self,notif):
        StateElem.update(self)
        self.data['myDAGrank']         = notif.myDAGrank

class StateTable(StateElem):

    def __init__(self,rowClass):
        StateElem.__init__(self)
        self.meta['rowClass']          = rowClass
        self.data['table']             = []

    def update(self,notif):
        StateElem.update(self)
        while len(self.data['table'])<notif.row+1:
            self.data['table'].append(self.meta['rowClass']())
        self.data['table'][notif.row].update(notif)

class moteState(MoteConnectorConsumer.MoteConnectorConsumer):
    
    ST_OUPUTBUFFER      = 'OutputBuffer'
    ST_ASN              = 'Asn'
    ST_MACSTATS         = 'MacStats'
    ST_SCHEDULEROW      = 'ScheduleRow'
    ST_SCHEDULE         = 'Schedule'
    ST_QUEUEROW         = 'QueueRow'
    ST_QUEUE            = 'Queue'
    ST_NEIGHBORSROW     = 'NeighborsRow'
    ST_NEIGHBORS        = 'Neighbors'
    ST_ISSYNC           = 'IsSync'
    ST_IDMANAGER        = 'IdManager'
    ST_MYDAGRANK        = 'MyDagRank'
    
    def __init__(self,moteConnector):
        
        # log
        log.debug("create instance")
        
        # store params
        self.moteConnector                  = moteConnector
        
        # initialize parent class
        MoteConnectorConsumer.MoteConnectorConsumer.__init__(self,self.moteConnector,
                                                                  [self.moteConnector.TYPE_STATUS],
                                                                  self._receivedData_notif)
        
        # local variables
        self.parserStatus                   = ParserStatus.ParserStatus()
        self.stateLock                      = threading.Lock()
        self.state                          = {}
        
        self.state[self.ST_OUPUTBUFFER]     = StateOutputBuffer()
        self.state[self.ST_ASN]             = StateAsn()
        self.state[self.ST_MACSTATS]        = StateMacStats()
        self.state[self.ST_SCHEDULE]        = StateTable(StateScheduleRow)
        self.state[self.ST_QUEUE]           = StateQueue()
        self.state[self.ST_NEIGHBORS]       = StateTable(StateNeighborsRow)
        self.state[self.ST_ISSYNC]          = StateIsSync()
        self.state[self.ST_IDMANAGER]       = StateIdManager()
        self.state[self.ST_MYDAGRANK]       = StateMyDagRank()
        
        self.notifHandlers = {
                self.parserStatus.named_tuple[self.ST_OUPUTBUFFER]:
                    self.state[self.ST_OUPUTBUFFER].update,
                self.parserStatus.named_tuple[self.ST_ASN]:
                    self.state[self.ST_ASN].update,
                self.parserStatus.named_tuple[self.ST_MACSTATS]:
                    self.state[self.ST_MACSTATS].update,
                self.parserStatus.named_tuple[self.ST_SCHEDULEROW]:
                    self.state[self.ST_SCHEDULE].update,
                self.parserStatus.named_tuple[self.ST_QUEUEROW]:
                    self.state[self.ST_QUEUE].update,
                self.parserStatus.named_tuple[self.ST_NEIGHBORSROW]:
                    self.state[self.ST_NEIGHBORS].update,
                self.parserStatus.named_tuple[self.ST_ISSYNC]:
                    self.state[self.ST_ISSYNC].update,
                self.parserStatus.named_tuple[self.ST_IDMANAGER]:
                    self.state[self.ST_IDMANAGER].update,
                self.parserStatus.named_tuple[self.ST_MYDAGRANK]:
                    self.state[self.ST_MYDAGRANK].update,
            }
    
    #======================== public ==========================================
    
    def getStateElem(self,elemName):
        
        if elemName not in self.state:
            raise ValueError('No state called {0}'.format(elemName))
        
        self.stateLock.acquire()
        returnVal = copy.deepcopy(self.state[elemName])
        self.stateLock.release()
        
        return returnVal
    
    def getStateElemNames(self):
        
        self.stateLock.acquire()
        returnVal = self.state.keys()
        self.stateLock.release()
        
        return returnVal
    
    #======================== private =========================================
    
    def _receivedData_notif(self,notif):
        
        # log
        log.debug("received {0}".format(notif))
        
        # lock the state data
        self.stateLock.acquire()
        
        # call handler
        found = False
        for k,v in self.notifHandlers.items():
            if self._isnamedtupleinstance(notif,k):
                found = True
                v(notif)
                break
        
        # unlock the state data
        self.stateLock.release()
        
        if found==False:
            raise SystemError("No handler for notif {0}".format(notif))
    
    def _isnamedtupleinstance(self,var,tupleInstance):
        return var._fields==tupleInstance._fields