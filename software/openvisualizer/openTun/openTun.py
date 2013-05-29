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

# IPv6 address for TUN interface
IPV6PREFIX = [0xbb,0xbb,0x00,0x00,0x00,0x00,0x00,0x00]
IPV6HOST   = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01]

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
        if   os.name=='nt':
            self.openTun         = openTunWindows.OpenTunWindows()
        elif os.name=='posix':
            self.openTun         = openTunLinux.OpenTunLinux()        
        else:
            raise NotImplementedError('OS {0} not supported'.format(os.name))
    
    #======================== public ==========================================
    
  
