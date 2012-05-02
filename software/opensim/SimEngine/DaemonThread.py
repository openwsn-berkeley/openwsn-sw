#!/usr/bin/python

import threading
import socket
import logging

from MoteHandler import MoteHandler

TCPCONN_MAXBACKLOG = 1       # the max number of unserved TCP connections

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class DaemonThread(threading.Thread):
    '''
    \brief Thread waiting for new connections from motes over TCP.
    '''
    
    def __init__(self,engine,port):
        
        # store variables
        self.engine    = engine
        self.port      = port
        
        # logging
        self.log   = logging.getLogger('DaemonThread')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('DaemonThread')
        
        # thread daemon mode
        self.setDaemon(True)
    
    def run(self):
        
        # log
        self.log.info('starting on port='+str(self.port))
        
        # create socket to listen on
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('',self.port))
            self.socket.listen(TCPCONN_MAXBACKLOG)
        except Exception as err:
            self.log.debug('could not start listening, err='+str(err))
        
        self.log.debug('listening')
        
        while True:
            
            # the daemon stops here while waiting for a user to connect
            conn,addr = self.socket.accept()
            
            # log connection attempt
            self.log.info("Connection attempt from "+str(addr))
            
            # hand over connection to moteHandler
            moteHandler = MoteHandler(self.engine,conn,addr[0],addr[1])
            
            # indicate to the engine the new mote's handler
            self.engine.indicateNewMote(moteHandler)
            
            # start the new mote handler
            moteHandler.start()
