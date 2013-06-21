import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('OVtracer')
log.setLevel(logging.DEBUG)
log.addHandler(NullHandler())


import threading
import yappi

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
              