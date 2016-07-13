#!/usr/bin/python
# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import sys
import os

if __name__=="__main__":
    # Update pythonpath if running in in-tree development mode
    basedir  = os.path.dirname(__file__)
    confFile = os.path.join(basedir, "openvisualizer.conf")
    if os.path.exists(confFile):
        import pathHelper
        pathHelper.updatePath()

import logging
log = logging.getLogger('openVisualizerCli')

try:
    from openvisualizer.moteState import moteState
except ImportError:
    # Debug failed lookup on first library import
    print 'ImportError: cannot find openvisualizer.moteState module'
    print 'sys.path:\n\t{0}'.format('\n\t'.join(str(p) for p in sys.path))

from   cmd         import Cmd
import openVisualizerApp
import openvisualizer.openvisualizer_utils as u


class OpenVisualizerCli(Cmd):
        
    def __init__(self,app):
        log.info('Creating OpenVisualizerCli')
        
        # store params
        self.app                    = app
        
        Cmd.__init__(self)
        self.doc_header = 'Commands (type "help all" or "help <topic>"):'
        self.prompt     = '> '
        self.intro      = '\nOpenVisualizer  (type "help" for commands)'
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def do_state(self, arg):
        """
        Prints provided state, or lists states.
        Usage: state [state-name]
        """
        if not arg:
            for ms in self.app.moteStates:
                output  = []
                output += ['Available states:']
                output += [' - {0}'.format(s) for s in ms.getStateElemNames()]
                self.stdout.write('\n'.join(output))
            self.stdout.write('\n')
        else:
            for ms in self.app.moteStates:
                try:
                    self.stdout.write(str(ms.getStateElem(arg)))
                    self.stdout.write('\n')
                except ValueError as err:
                    self.stdout.write(err)
    
    def do_list(self, arg):
        """List available states. (Obsolete; use 'state' without parameters.)"""
        self.do_state('')
    
    def do_root(self, arg):
        """
        Sets dagroot to the provided mote, or lists motes
        Usage: root [serial-port]
        """
        if not arg:
            self.stdout.write('Available ports:')
            if self.app.moteStates:
                for ms in self.app.moteStates:
                    self.stdout.write('  {0}'.format(ms.moteConnector.serialport))
            else:
                self.stdout.write('  <none>')
            self.stdout.write('\n')
        else:
            for ms in self.app.moteStates:
                try:
                    if ms.moteConnector.serialport==arg:
                        ms.triggerAction(moteState.moteState.TRIGGER_DAGROOT)
                except ValueError as err:
                    self.stdout.write(err)
    
    def do_set(self,arg):
        """
        Sets mote with parameters
        Usag
        """
        if not arg:
            self.stdout.write('Available ports:')
            if self.app.moteStates:
                for ms in self.app.moteStates:
                    self.stdout.write('  {0}'.format(ms.moteConnector.serialport))
            else:
                self.stdout.write('  <none>')
            self.stdout.write('\n')
        else:
            try:
                [port,command,parameter] = arg.split(' ')
                for ms in self.app.moteStates:
                    try:
                        if ms.moteConnector.serialport==port:
                            ms.triggerAction([moteState.moteState.SET_COMMAND,command,parameter])
                    except ValueError as err:
                        self.stdout.write(err)
            except ValueError as err:
                print "{0}:{1}".format(type(err),err)

    def help_all(self):
        """Lists first line of help for all documented commands"""
        names = self.get_names()
        names.sort()
        maxlen = 65
        self.stdout.write(
            'type "help <topic>" for topic details\n'.format(80-maxlen-3))
        for name in names:
            if name[:3] == 'do_':
                try:
                    doc = getattr(self, name).__doc__
                    if doc:
                        # Handle multi-line doc comments and format for length.
                        doclines = doc.splitlines()
                        doc      = doclines[0]
                        if len(doc) == 0 and len(doclines) > 0:
                            doc = doclines[1].strip()
                        if len(doc) > maxlen:
                            doc = doc[:maxlen] + '...'
                        self.stdout.write('{0} - {1}\n'.format(
                                                name[3:80-maxlen], doc))
                except AttributeError:
                    pass
    
    def do_quit(self, arg):
        self.app.close()
        return True

    def emptyline(self):
        return


#============================ main ============================================

if __name__=="__main__":
    app = openVisualizerApp.main()
    app.eventBusMonitor.setWiresharkDebug(True)
    cli = OpenVisualizerCli(app)
    cli.cmdloop()
