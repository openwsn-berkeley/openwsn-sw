#!/usr/bin/python

import sys
import threading
import logging
import binascii
import time

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class SimCli(threading.Thread):
    '''
    \brief Thread which handles CLI commands entered by the user.
    '''
    
    def __init__(self):
    
        # record variables
        
        # local variables
        self.commands = []
        
        # register commands
        self._registerCommand('help', 
                              'h',
                              'print this menu',
                              '',
                              self._handleHelp)
        self._registerCommand('poipoi',
                              'p',
                              'poipoi',
                              '<poipoi> <poipoi>',
                              self._handlePoipoi)
        self._registerCommand('quit',
                              'q',
                              'quit this application',
                              '',
                              self._handleQuit)
        
        # logging
        self.log           = logging.getLogger('SimCli')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # set thread name
        self.setName('SimCli')
        
        # thread daemon mode
        self.setDaemon(False)
        
    def run(self):
        print 'OpenSim server\n'
        
        while True:
            
            params = raw_input('> ')
            
            self.log.debug('Following command entered:'+params)
            
            params = params.split()
            if len(params)<1:
                continue
                
            if len(params)==2 and params[1]=='?':
                if not self._printUsageFromName(params[0]):
                    if not self._printUsageFromAlias(params[0]):
                        print ' unknown command or alias \''+params[0]+'\''
                continue

            found = False
            for command in self.commands:
                if command['name']==params[0] or command['alias']==params[0]:
                    found = True
                    command['callback'](params[1:])
                    break
            
            if found==False:
                print ' unknown command or alias \''+params[0]+'\''
    
    #======================== private =========================================
    
    def _registerCommand(self,name,alias,description,usage,callback):
        self.commands.append({
                                'name':          name,
                                'alias':         alias,
                                'description':   description,
                                'usage':         usage,
                                'callback':      callback,
                             })
    
    def _printUsageFromName(self,commandname):
        for command in self.commands:
            if command['name']==commandname:
                print 'usage: '+commandname+' '+command['usage']
                return True
        return False
    
    def _printUsageFromAlias(self,commandalias):
        for command in self.commands:
            if command['alias']==commandalias:
                print 'usage: '+commandalias+' '+command['usage']
                return True
        return False
    
    #=== command handlers
    
    def _handleHelp(self,params):
        # usage
        if len(params)!=0:
            self._printUsageFromName('help')
            return
        
        output  = '\n'
        output  = ' Available commands:\n'
        for command in self.commands:
            output += '   '+command['name']+' ('+command['alias']+')'+' - '+command['description']+'\n'
        output += ' Notes:\n'
        output += '  - type \'<command> ?\' to get the usage\n'
        print output
    
    def _handlePoipoi(self,params):
        print "poipoi"
    
    def _handleQuit(self,params):
        
        # usage
        if len(params)!=0:
            self._printUsageFromName('quit')
            return
        
    def _handleQuit(self,params):
        
        # usage
        if len(params)!=0:
            self._printUsageFromName('quit')
            return
        
        # disconnect all users
        self.lbrd.disconnectUser(Lbrd.Lbrd.ALL)
        
        # this thread quits
        sys.exit(0)
    
    #======================== helpers =========================================