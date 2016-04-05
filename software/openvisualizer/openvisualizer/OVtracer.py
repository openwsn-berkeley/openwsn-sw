# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('OVtracer')
log.setLevel(logging.DEBUG)
log.addHandler(logging.NullHandler())

import yappi
import threading

class OVtracer(object):
    TRACING_INTERVAL = 30
    
    def __init__(self):
            yappi.start()
            self.timer = threading.Timer(self.TRACING_INTERVAL,self._logTracingStats)
            self.timer.start()
            
    def _logTracingStats(self):
         yappi.enum_thread_stats(self._logThreadStat)
         #yappi.enum_stats(self._logFunctionStat)
         self.timer = threading.Timer(self.TRACING_INTERVAL,self._logTracingStats)
         self.timer.start()
         
    def _logThreadStat(self,stat_entry):
         log.info("Thread Trace: {0}".format(stat_entry))
         #print "Thread Trace: {0}".format(stat_entry)
    
    def _logFunctionStat(self,stat_entry):
         log.info("Function Trace: {0}".format(stat_entry))
         #print "Function Trace: {0}".format(stat_entry)
              