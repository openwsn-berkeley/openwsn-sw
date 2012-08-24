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
from Event     import Event
from Callback  import Callback
#from threading import Thread
import threading
import time

""" A singleton """
class EventBus(threading.Thread):
    _instance = None
    _init = False
    
    """ override creation of the object so it is create only once.. singleton pattern """
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventBus, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    """  after new, initialization """
    def __init__(self):
        if (self._init):
            return
        threading.Thread.__init__(self)
        self.__pending_events = []
        self.__callbacks      = {}
        self.__next_id        = 1
        self._init = True
        self.start()  #Start async handling.

    def run(self): 
        log.info("EventBus asynch event handling running")
        while len(self.__pending_events) > 0:
            event = self.__pending_events.pop(0)
            log.info("EventBus notifies {0}".format(event.get_uri()))
            self.emit_sync(event.get_uri(), event.get_args())

    def add_listener(self, callback):
        """
        Adds a listener to the event bus. The given function is called whenever
        any event is sent that matches the given regular expression. If no
        regular expression was given, any signal is emitted.
        @type  callback: Callback
        @param callback: Specifies the requested notification.
        @rtype:  Boolean
        @return: False if the listener was not found, True otherwise.
        """
        assert callback is not None
        self.__callbacks[str(self.__next_id)] = callback
        assert self.__next_id < sys.maxint
        self.__next_id += 1
        log.info("EventBus listener added {0}".format(callback.get_event_uri()))
        return self.__next_id - 1

    def remove_listener_from_id(self, id):
        """
        Removes a listener from the event bus.
        @type  id: integer
        @param id: The id of the listener to remove.
        @rtype:  Boolean
        @return: False if the listener was not found, True otherwise.
        """
        assert id > 0
        if not self.__callbacks.has_key(str(id)):
            return False
        del self.__callbacks[id]
        log.info("EventBus removed {0}".format(id))
        return True
    
    """ Invoke asynchronous"""
    def emit(self, uri, args = None):
        assert uri is not None
        event = Event(uri, args)
        self.__pending_events.append(event)
        log.info("EventBus new asynch event {0}".format(uri))

    """ Invoke synchronous"""
    def emit_sync(self, uri, args = None):
        assert uri is not None
        log.info("EventBus new synch event {0}".format(uri))
        for id in self.__callbacks:
            callback = self.__callbacks[id]
            if callback.matches_uri(uri):
                func     = callback.get_function()
                func(args)  
                
                
    def test(self):
        bus=EventBus()
        callback=Callback(self.test_print,"test")
        bus.add_listener(callback)
        bus.emit("test","1")
        time.sleep(2)
        bus.emit_sync("test","2")
        
        print "end"
                    
    def test_print(self,args):
        print "bang bang! "+args
        
if __name__=="__main__":
    EventBus().test() 
    time.sleep(4)            