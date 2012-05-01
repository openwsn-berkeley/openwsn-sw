#!/usr/bin/python

import threading
import socket
import logging
import os
import time

from BspEmulator import BspBoard
from BspEmulator import BspBsp_timer
from BspEmulator import BspDebugpins
from BspEmulator import BspEui64
from BspEmulator import BspLeds
from BspEmulator import BspRadio
from BspEmulator import BspRadiotimer
from BspEmulator import BspUart

TCPRXBUFSIZE       = 4096    # size of the TCP reception buffer

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class OpenSimProto(object):
    '''
    \brief Handle the connection of a mote.
    '''
    
    def __init__(self,conn,addr,port):
        
        # store params
        self.conn                 = conn
        self.addr                 = addr
        self.port                 = port
        
        # local variables
        self.waitingForReplySem   = threading.Lock()
        self.waitingForReply      = False
        
        # bsp components
        self.bspBoard             = BspBoard.BspBoard()
        self.bspBsp_timer         = BspBsp_timer.BspBsp_timer()
        self.bspDebugpins         = BspDebugpins.BspDebugpins()
        self.bspEui64             = BspEui64.BspEui64()
        self.bspLeds              = BspLeds.BspLeds()
        self.bspRadio             = BspRadio.BspRadio()
        self.bspRadiotimer        = BspRadiotimer.BspRadiotimer()
        self.bspUart              = BspUart.BspUart()
        
        # logging
        self.log   = logging.getLogger('MoteHandler')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('MoteHandler')
        
        # thread daemon mode
        self.setDaemon(True)
    
    def run(self):
    
        # log
        self.log.info('starting')
        
        self.conn.send('poipoi')
        
        while(1):
            try:
                input = self.conn.recv(TCPRXBUFSIZE)
            except socket.error as err:
                self.log.critical('connection error (err='+str(err)+')')
                break
            
            self.log.info('received input='+str(input))
            if self.waitingForReply:
                self.log.debug('This is a reply.')
                self.response = input
                self.waitingForReplySem.release()
            else:
                self.log.debug('This is a response.')
                self._handleReceivedCommand(input)
    
    #======================== public ==========================================
    
    def sendCommand(send,dataToSend):
        self.conn.send(dataToSend)
        self.waitingForReply = True
        self.waitingForReplySem.acquire()
    
    #======================== private =========================================
    
    def _handleReceivedCommand(self,input):
        time.sleep(1)
        
        print ord(input[0])
        
        self.conn.send(chr(0))