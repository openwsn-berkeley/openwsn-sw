#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.join(sys.path[0], '..'))

import time
import pprint
import logging
import logging.handlers

import pytest

import EventBus

#============================ logging =========================================

LOGFILE_NAME = 'test_sync.log'

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('test_sync')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

logHandler = logging.handlers.RotatingFileHandler(LOGFILE_NAME,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['test_sync',
                   'EventBus',]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)

#============================ helpers =========================================

class Subscriber(object):
    def __init__(self,name):
        self.name         = name
        self.resetNotifications()
    
    def notification_singleText(self,publishedText):
        
        # log
        log.debug("{0} notification_singleText publishedText={1}".format(self.name,
                                                                   publishedText))
        
        assert isinstance(publishedText,str)
        
        self.notifications['text'].append(publishedText)
    
    def notification_doubleNum(self,num1,num2):
        
        # log
        log.debug("{0} notification_doubleNum num1={1} num2={2}".format(
            self.name,
            num1,
            num2))
        
        assert isinstance(num1,int)
        assert isinstance(num2,int)
        
        self.notifications['num'].append((num1,num2))
    
    def resetNotifications(self):
        self.notifications = {
            'text': [],
            'num':  [],
        }

def prettyformat(dataToPrint):
    pp = pprint.PrettyPrinter(indent=4)
    return pp.pformat(dataToPrint)
    
#============================ tests ===========================================

global subscriber1
global subscriber2

#----- setup

def test_setup():
    global bus
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_init")
    
    bus = EventBus.EventBus()
    
    assert bus
    assert isinstance(bus,EventBus.EventBus)
    assert bus.getSubscriptions()=={}

#---- subscription
    
def test_subscribe_both():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_subscribe_both")
    
    subscriber1 = Subscriber('subscriber1')
    subscriber2 = Subscriber('subscriber2')
    
    EventBus.EventBus().subscribe(subscriber1.notification_singleText,'text')
    EventBus.EventBus().subscribe(subscriber1.notification_doubleNum,'num')
    EventBus.EventBus().subscribe(subscriber2.notification_singleText,'text')
    EventBus.EventBus().subscribe(subscriber2.notification_doubleNum,'num')
    
    # log
    log.debug(prettyformat(bus.getSubscriptions()))
    
    assert len(bus.getSubscriptions().keys())==4

#---- text publication

def test_publishText_sync_both():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_publishText_sync_both")
    
    EventBus.EventBus().publish_sync('text','someText1')
    
    # log
    log.debug(prettyformat(subscriber1.notifications))
    log.debug(prettyformat(subscriber2.notifications))
    
    assert subscriber1.notifications=={
        'text': ['someText1'],
        'num':  [],
    }
    assert subscriber2.notifications=={
        'text': ['someText1'],
        'num':  [],
    }

def test_publishText_sync_both_again():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_publishText_sync_both_again")
    
    EventBus.EventBus().publish_sync('text','someText2')
    
    assert subscriber1.notifications=={
        'text': ['someText1','someText2'],
        'num':  [],
    }
    assert subscriber2.notifications=={
        'text': ['someText1','someText2'],
        'num':  [],
    }

def test_publishText_async_both():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_publishText_async_both")
    
    EventBus.EventBus().publish('text','someText3')
    
    time.sleep(1) # longest possible time for thread to publish
    
    assert subscriber1.notifications=={
        'text': ['someText1','someText2','someText3'],
        'num':  [],
    }
    assert subscriber2.notifications=={
        'text': ['someText1','someText2','someText3'],
        'num':  [],
    }

def test_publishText_async_both_again():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_publishText_async_both_again")
    
    EventBus.EventBus().publish('text','someText4')
    
    time.sleep(1) # longest possible time for thread to publish
    
    assert subscriber1.notifications=={
        'text': ['someText1','someText2','someText3','someText4'],
        'num':  [],
    }
    assert subscriber2.notifications=={
        'text': ['someText1','someText2','someText3','someText4'],
        'num':  [],
    }

def test_publishNum_sync_both():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_publishNum_sync_both")
    
    EventBus.EventBus().publish_sync('num',1,2)
    
    # log
    log.debug(prettyformat(subscriber1.notifications))
    log.debug(prettyformat(subscriber2.notifications))
    
    assert subscriber1.notifications=={
        'text': ['someText1','someText2','someText3','someText4'],
        'num':  [(1,2)],
    }
    assert subscriber2.notifications=={
        'text': ['someText1','someText2','someText3','someText4'],
        'num':  [(1,2)],
    }

#---- unsubscription

def test_unsubscription():
    global subscriber1
    global subscriber2
    
    res = EventBus.EventBus().unsubscribe(3)
    assert res
    res = EventBus.EventBus().unsubscribe(4)
    assert res
    
    # log
    log.debug(prettyformat(EventBus.EventBus().getSubscriptions()))
    
    EventBus.EventBus().publish_sync('text','someText5')
    EventBus.EventBus().publish_sync('num',3,4)
    
    # log
    log.debug(prettyformat(subscriber1.notifications))
    log.debug(prettyformat(subscriber2.notifications))
    
    assert subscriber1.notifications=={
        'text': ['someText1','someText2','someText3','someText4','someText5'],
        'num':  [(1,2),(3,4)],
    }
    assert subscriber2.notifications=={
        'text': ['someText1','someText2','someText3','someText4'],
        'num':  [(1,2)],
    }

#----- teardown

def test_teardown():
    global subscriber1
    global subscriber2
    
    log.debug("\n\n----------test_teardown")
    
    EventBus.EventBus().close()