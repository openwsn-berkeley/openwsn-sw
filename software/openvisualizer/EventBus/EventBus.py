'''
Created on 24/08/2012

@author: xvilajosana
'''
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('EventBus')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())

import sys
import threading
import time

import Subscription
import Event

class EventBus(threading.Thread):
    '''
    \brief An event bus to which modules can publish/subscribe.
    
    It is implemented as a singleton, i.e. only one instance of the eventBus
    lives in the system. This means that separate modules can instantiate this
    class independently and publish/subscribe to the result of that
    instantiation.
    '''
    _instance      = None
    _init          = False
    
    def __new__(cls, *args, **kwargs):
        '''
        \brief Override creation of the object so it is create only once
               (singleton pattern)
        '''
        if not cls._instance:
            cls._instance = super(EventBus, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        '''
        \brief Initializer.
        
        \note This function is called after __new__.
        '''
        
        if self._init:
            return
        
        # log
        log.debug("initialize instance")
        
        # intialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'eventBus'
        
        # local variables
        self._eventSem            = threading.Semaphore(0)
        self._pending_events      = []      ##< list of pending events
        self._subscriptions       = {}      ##< list of subscriptions
        self._next_id             = 1       ##< index of a new element in _subscriptions
        self._init                = True    ##< this object was initialized
        
        # start asynchronous handling
        self.start()

    def run(self): 
        # log
        log.debug("thread running")
        
        try:
            while True:
                
                # block until at least one event is in the pending events
                self._eventSem.acquire()
                
                # pop the head event
                event = self._pending_events.pop(0)
                
                if   isinstance(event,Event.Event):
                    # normal case
                
                    # log
                    log.debug("popped event {0} ".format(event))
                    
                    # publish
                    
                    self.publish_sync(event.get_uri(),
                                      *event.get_args(),
                                      minNumReceivers=event.get_minNumReceivers(),
                                      maxNumReceivers=event.get_maxNumReceivers())
                    
                elif (instance(event,str)) and (event=='close'):
                    # teardown case
                    
                    # log
                    log.debug("...closed.")
                    
                    return
                
                else:
                    
                    # log
                    log.critical("unexpected event={0}".format(event))
                    
                    raise SystemError()
        except Exception as err:
            log.critical(err)
            raise
    
    #======================== public ==========================================
    
    def subscribe(self, func, uri=None):
        '''
        \brief Adds a subscriber to the event bus.
        
        The given function pointer passed is called whenever an event is sent
        that matches the given regular expression. If no regular expression
        was given, the function is called for any emitted signal.
        
        \param func The function to call.
        \param uri  The URI trigger this fuction to be called.
        
        \returns The unique identifier of this registration, an int. The caller
                 can store and use that ID to unsubscribe.
        '''
        
        # param validation
        assert callable(func)
        if uri:
            assert isinstance(uri,str)
        
        # create the Subscription instance
        subs = Subscription.Subscription(func,uri)
        
        # get a unique ID for that subscriber
        id = self._getNextId()
        
        # store subs
        self._subscriptions[id] = subs
        
        # log
        log.info("subscriber added: {0} -> {1}".format(
                subs.get_event_uri(),
                subs.get_function(),
            )
        )
        
        return id

    def unsubscribe(self, id):
        '''
        \brief Removes a subscriber from the event bus.
        
        \param   The id of the subscriber to remove, an int.
        
        \returns True if the subscriber was found (and removed).
        \returns False if the subscriber was not found.
        '''
        
        # param validation
        assert isinstance(id,int)
        assert id > 0
        
        if id in self._subscriptions:
            
            # log 
            log.info("removed subscriber id {0}".format(id))
            
            # delete
            del self._subscriptions[id]
        
            return True
            
        else:
            
            # log 
            log.warning("could not find subscriber id {0} to remove".format(id))
            
            return False
        
        raise SystemError()
    
    def publish(self, uri, *args, **kwargs):
        '''
        \brief Publish an event.
        
        Publication is done asynchronously by the eventBus thread, i.e.
        sometimes after this function is called.
        
        \param uri  The URI of the published event.
        \param args The arguments to pass to the callback function
        '''
        # log
        log.debug("publish uri={0} args={1} kwargs={2}".format(uri,args,kwargs))
        
        # param validation
        assert uri
        assert isinstance(uri,str)
        if 'minNumReceivers' in kwargs:
            assert isinstance(kwargs['minNumReceivers'],int)
        if 'maxNumReceivers' in kwargs:
            assert isinstance(kwargs['maxNumReceivers'],int)
        
        self._pending_events.append(Event.Event(uri, args))
        self._eventSem.release()
    
    def publish_sync(self, uri, *args, **kwargs):
        '''
        \brief Publish an event synchronously.
        
        Publication is done before this function returns.
        
        \param uri  The URI of the published event.
        \param args The arguments to pass to the callback function
        '''
        # log
        log.debug("publish_sync uri={0} args={1} kwargs={2}".format(uri,args,kwargs))
        
        # param validation
        assert uri
        assert isinstance(uri,str)
        if ('minNumReceivers' in kwargs) and kwargs['minNumReceivers']:
            assert isinstance(kwargs['minNumReceivers'],int)
        if ('maxNumReceivers' in kwargs) and kwargs['maxNumReceivers']:
            assert isinstance(kwargs['maxNumReceivers'],int)
        
        # local variables
        self.numReceivers = 0
        
        # publish to subscribers
        for (id,subs) in self._subscriptions.items():
            if subs.matches_uri(uri):
                subs.get_function()(*args)
                self.numReceivers += 1
        
        # ensure that number receivers is expected
        if ('minNumReceivers' in kwargs) and kwargs['minNumReceivers']:
            if self.numReceivers<kwargs['minNumReceivers']:
                raise SystemError('expected a least {0} receivers for event {1}, got {2}'.format(
                                kwargs['minNumReceivers'],
                                uri,
                                self.numReceivers,
                            )
                        )
        if ('maxNumReceivers' in kwargs) and kwargs['maxNumReceivers']:
            if self.numReceivers>kwargs['maxNumReceivers']:
                raise SystemError('expected a most {0} receivers for event {1}, got {2}'.format(
                                kwargs['maxNumReceivers'],
                                uri,
                                self.numReceivers,
                            )
                        )
    
    def getSubscriptions(self):
        '''
        \brief Retrieve the current list of subscriptions.
        
        \returns The current list of subscriptions, as a dictionary of
                 dictionaries:
                 
                 returnVal = {
                    1: {
                          'uri':      'someURI'
                          'function': cb_function
                    },
                    etc.
                 }
        
        '''
        returnVal = {}
        for (id,subs) in self._subscriptions.items():
            returnVal[id] = {
                'uri':      subs.get_event_uri(),
                'function': subs.get_function(),
            }
        return returnVal
    
    def close(self):
        '''
        \brief Destroy this eventBus.
        
        \note This also stops the thread.
        '''
        
        # log
        log.debug("closing...")
        
        self._pending_events.append('close')
        self._eventSem.release()
    
    #======================== private =========================================
    
    def _getNextId(self):
        retunVal = self._next_id
        assert self._next_id < sys.maxint
        self._next_id += 1
        return retunVal
