#!/usr/bin/python

import threading
import socket
import logging
import os

TCPRXBUFSIZE       = 4096    # size of the TCP reception buffer

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class MoteHandler(threading.Thread):
    '''
    \brief Handle the connection of a new mote.
    '''
    
    def __init__(self,conn,addr,port):
        
        # store params
        self.conn  = conn
        self.addr  = addr
        self.port  = port
        
        # local variables
        
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
    
    #======================== public ==========================================
    
    def run(self):
    
        # log
        self.log.info('starting')
        
        while(1):
            try:
                input = self.conn.recv(TCPRXBUFSIZE)
            except socket.error as err:
                self.log.error('connection error (err='+str(err)+')')
            else:
                self.log.info('received input='+str(input))
            self.conn.send('poipoipoipoi')
    
    #======================== private =========================================
    