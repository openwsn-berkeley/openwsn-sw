import os
if os.name=='nt':       #windows
   import _winreg as winreg
elif os.name=='posix':  #linux
   import glob

def findSerialPortsNames():
    '''
    \brief Return the names of the serial ports a mote is connected to.
    
    \returns A list of strings, each representing a serial port.
             E.g. ['COM1', 'COM2']
    '''
    serialport_names = []
    if os.name=='nt':
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        for i in range(winreg.QueryInfoKey(key)[1]):
            try:
                val = winreg.EnumValue(key,i)
            except:
                pass
            else:
                if ( (val[0].find('VCP')>-1) or (val[0].find('Silabser')>-1) ):
                    serialport_names.append(str(val[1]))
    elif os.name=='posix':
        serialport_names = glob.glob('/dev/ttyUSB*')
    serialport_names.sort()
    return serialport_names