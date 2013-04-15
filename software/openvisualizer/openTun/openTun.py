import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('OpenTun')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import os

if os.name=='nt':
   import openTunWindows
elif os.name=='posix':
   import openTunLinux

class OpenTun():
    '''
    \brief Class which interfaces between a TUN virtual interface and an
        EventBus.
    '''
    
    def __init__(self):
        
        # log
        log.debug("create instance")
        self.openTun         = None
        
        # store params
        if os.name=='nt':
            self.openTun         = openTunWindows.OpenTunWindows()
        elif os.name=='posix':
            self.openTun         = openTunLinux.OpenTunLinux()        
    
    #======================== public ==========================================
    
  