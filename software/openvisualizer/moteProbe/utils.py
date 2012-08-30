import os
if os.name=='nt':       # Windows
   import _winreg as winreg
elif os.name=='posix':  # Linux
   import glob

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbeUtils')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

BAUDRATE_TELOSB = 115200 # poipoipoi
BAUDRATE_GINA   = 115200

def findSerialPorts():
    '''
    \brief Returns the serial ports of the motes connected to the computer.
    
    \returns A list of tuples (name,baudrate) where:
            - name is a strings representing a serial port, e.g. 'COM1'
            - baudrate is an int representing the baurate
    '''
    serialports = []
    
    if os.name=='nt':
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        for i in range(winreg.QueryInfoKey(key)[1]):
            try:
                val = winreg.EnumValue(key,i)
            except:
                pass
            else:
                if   val[0].find('VCP')>-1:
                    serialports.append( (str(val[1]),BAUDRATE_TELOSB) )
                elif val[0].find('Silabser')>-1:
                    serialports.append( (str(val[1]),BAUDRATE_GINA) )
    elif os.name=='posix':
        serialports = [(s,BAUDRATE_GINA) for s in glob.glob('/dev/ttyUSB*')]
    
    # log
    log.debug("discovered following COM port: {0}".format(['{0}@{1}'.format(s[0],s[1]) for s in serialports]))
    
    return serialports