import sys
import os
import struct
import binascii
if __name__=='__main__':
    cur_path = sys.path[0]
    sys.path.insert(0, os.path.join(cur_path, '..', '..'))                     # openvisualizer/
    sys.path.insert(0, os.path.join(cur_path, '..', '..', '..', 'openCli'))    # openCli/
    
import logging 
class NullHandler(logging.Handler): 
    def emit(self, record): 
        pass 
log = logging.getLogger('MoteStateCli') 
log.setLevel(logging.DEBUG) 
log.addHandler(NullHandler()) 

from moteProbe     import moteProbe
from moteConnector import moteConnector
from moteState     import moteState
from OpenCli       import OpenCli

LOCAL_ADDRESS  = '127.0.0.1'
TCP_PORT_START = 8090

class MoteStateCli(OpenCli):
    
    def __init__(self,moteProbe_handlers,moteConnector_handlers,moteState_handlers):
        
        # store params
        self.moteProbe_handlers     = moteProbe_handlers
        self.moteConnector_handlers = moteConnector_handlers
        self.moteState_handlers     = moteState_handlers
    
        # initialize parent class
        OpenCli.__init__(self,"Reservation Experiment CLI",self._quit_cb)
        
        # add commands
        self.registerCommand('list',
                             'l',
                             'list available states',
                             [],
                             self._handlerList)
        self.registerCommand('state',
                             's',
                             'prints some state',
                             ['state parameter'],
                             self._handlerState)
        self.registerCommand('reserve',
                             'r',
                             'reserve cells; e.g. "r e6 eb 2 10032"',
                             ['mote_addr','neighbor_addr','num_of_links','start_at_asn'],
                             self._handlerRes)

    #======================== public ==========================================
    
    #======================== private =========================================
    
    #===== callbacks
    
    def _handlerList(self,params):
        for ms in self.moteState_handlers:
            output  = []
            output += ['available states:']
            output += [' - {0}'.format(s) for s in ms.getStateElemNames()]
            print '\n'.join(output)
    
    def _handlerState(self,params):
        for ms in self.moteState_handlers:
            try:
                print ms.getStateElem(params[0])
            except ValueError as err:
                print err

    def _handlerRes(self,params):
        for ms in self.moteState_handlers:
            try:
                myid = str(ms.getStateElem("IdManager").data[0]['my16bID'])
                myid=myid[3:5]
                if myid==params[0]:#match the ID and then send command to mote
                   print(params)
                   input  = struct.pack('<BBH',(int(params[1],16)),(int(params[2])),(int(params[3])))
                   ms.moteConnector.write(input,headerByte='Q') 
            except ValueError as err:
                print err
    
    #===== helpers
    
    def _quit_cb(self):
        
        for mc in self.moteConnector_handlers:
           mc.quit()
        for mb in self.moteProbe_handlers:
           mb.quit()

def main():
    
    moteProbe_handlers     = []
    moteConnector_handlers = []
    moteState_handlers     = []
    
    # create a moteProbe for each mote connected to this computer
    serialPorts    = moteProbe.utils.findSerialPorts()
    tcpPorts       = [TCP_PORT_START+i for i in range(len(serialPorts))]
    for (serialPort,tcpPort) in zip(serialPorts,tcpPorts):
        moteProbe_handlers.append(moteProbe.moteProbe(serialPort,tcpPort))
    
    # create a moteConnector for each moteProbe
    for mp in moteProbe_handlers:
       moteConnector_handlers.append(moteConnector.moteConnector(LOCAL_ADDRESS,mp.getTcpPort()))
    
    # create a moteState for each moteConnector
    for mc in moteConnector_handlers:
       moteState_handlers.append(moteState.moteState(mc))
    
    # create an open CLI
    cli = MoteStateCli(moteProbe_handlers,
                       moteConnector_handlers,
                       moteState_handlers)
    
    # start threads
    for ms in moteState_handlers:
       ms.start()
    for mc in moteConnector_handlers:
       mc.start()
    cli.start()
    
#============================ application logging =============================
import logging
import logging.handlers
logHandler = logging.handlers.RotatingFileHandler('moteStateCli.log',
                                                  maxBytes=2000000,
                                                  backupCount=5,
                                                  mode='w')
logHandler.setFormatter(logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s"))
for loggerName in ['moteProbe',
                   'moteConnector',
                   'OpenParser',
                   'Parser',
                   'ParserStatus',
                   'ParserData',
                   'moteState',
                   'OpenCli',
                   ]:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)
    
if __name__=="__main__":
    main()