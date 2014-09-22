'''
This is a functional test which verify the correct behavior of the OpenTun.
The test involves 3 components:
- the openTun element under test, which sits on the EvenBus
- the ReadThread, implemented in this test module, which listens for ICMPv6
  echo request packets, and answers with an echo reply packet.
- the WriteThread, implemented in this test module, which periodically sends
  an echo reply. The expected behavior is that, for each echo request sent by
  the writeThread, an echo reply is received by the readThread.

Run this test by double-clicking on this file, then pinging any address in the
prefix of your tun interface (e.g. 'ping bbbb::5').
'''

import sys
import os
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','eventBus','PyDispatcher-2.0.3'))# PyDispatcher-2.0.3/
    sys.path.insert(0, os.path.join(here, '..', '..'))                                # openvisualizer/

import threading
import time
import traceback
import openvisualizer_utils as u


from eventBus import eventBusClient
from openTun  import openTun

#============================ defines =========================================

#============================ helpers =========================================

#=== misc

def carry_around_add(a, b):
    '''
    \brief Helper function for checksum calculation.
    '''
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(byteList):
    '''
    \brief Calculate the checksum over a byte list.
    
    This is the checksum calculation used in e.g. the ICMPv6 header.
    
    \return The checksum, a 2-byte integer.
    '''
    s = 0
    for i in range(0, len(byteList), 2):
        w = byteList[i] + (byteList[i+1] << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

#============================ threads =========================================

class ReadThread(eventBusClient.eventBusClient):
    '''
    \brief Thread which continously reads input from a TUN interface.
    
    If that input is an IPv4 or IPv6 echo request (a "ping" command) issued to
    any IP address in the virtual network behind the TUN interface, this thread
    answers with the appropriate echo reply.
    '''
    
    def __init__(self):
        
        # store params
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'OpenTun',
            registrations         = [
                {
                    'sender'   : self.WILDCARD,
                    'signal'   : 'v6ToMesh',
                    'callback' : self._v6ToMesh_notif
                }
            ]
        )
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _v6ToMesh_notif(self,sender,signal,data):
        
        p = data
        
        assert (p[0]&0xf0)==0x60
        
        if p[6]==0x3a:
            # ICMPv6
            
            if p[40]==0x80:
                # IPv6 echo request
                
                # print
                print 'Received IPv6 echo request'
                
                # create echo reply
                echoReply = self._createIpv6EchoReply(p)
                
                # send over interface
                self.dispatch(
                    signal    = 'v6ToInternet',
                    data      = echoReply
                )
                
                # print
                print 'Transmitted IPv6 echo reply'
            
            elif p[40]==0x81:
                
                # print
                print 'Received IPv6 echo reply'
    
    def _createIpv6EchoReply(self,echoRequest):
        
        # invert addresses, change "echo request" type to "echo reply"
        echoReply       = echoRequest[:8]    + \
                          echoRequest[24:40] + \
                          echoRequest[8:24]  + \
                          [129]              + \
                          echoRequest[41:]
        
        # recalculate checksum
        pseudo          = []
        pseudo         += echoRequest[24:40]               # source address
        pseudo         += echoRequest[8:24]                # destination address
        pseudo         += [0x00]*3+[len(echoRequest[40:])] # upper-layer packet length
        pseudo         += [0x00]*3                         # zero
        pseudo         += [58]                             # next header
        pseudo         += echoRequest[40:]                 # ICMPv6 header+payload
        
        pseudo[40]      = 129                              # ICMPv6 type = echo reply
        pseudo[42]      = 0x00                             # reset CRC for calculation
        pseudo[43]      = 0x00                             # reset CRC for calculation
        
        crc             = checksum(pseudo)
        
        echoReply[42]   = (crc&0x00ff)>>0
        echoReply[43]   = (crc&0xff00)>>8
        
        return echoReply

class WriteThread(threading.Thread):
    '''
    \brief Thread with periodically sends IPv6 echo requests.
    '''
    
    SLEEP_PERIOD   = 1
    
    def __init__(self,dispatch):
    
        # store params
        self.dispatch = dispatch
        
        # local variables
        
        # initialize parent
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'writeThread'
        
        # start myself
        self.start()
    
    def run(self):
        try:
            while True:
                
                # sleep a bit
                time.sleep(self.SLEEP_PERIOD)
                
                # create an echo request
                echoRequest = self._createIPv6echoRequest()
                
                #
                
                # transmit
                self.dispatch(
                    signal    = 'v6ToInternet',
                    data      = echoRequest
                )
        except Exception as err:
            errMsg=u.formatCrashMessage(self.name,err)
            print errMsg
            log.critical(errMsg)
            sys.exit(1)
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _createIPv6echoRequest(self):
        '''
        \brief Create an IPv6 echo request.
        '''
        
        echoRequest  = []
        
        # IPv6 header
        echoRequest    += [0x60,0x00,0x00,0x00]       # ver, TF
        echoRequest    += [0x00, 40]                  # length
        echoRequest    += [58]                        # Next header (58==ICMPv6)
        echoRequest    += [128]                       # HLIM
        echoRequest    += [0xbb, 0xbb, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x05,]   # source
        echoRequest    += [0xbb, 0xbb, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x01,]   # destination
        
        # ICMPv6 header
        echoRequest    += [128]                       # type (128==echo request)
        echoRequest    += [0]                         # code
        echoRequest    += [0x00,0x00]                 # Checksum (to be filled out later)
        echoRequest    += [0x00,0x04]                 # Identifier
        echoRequest    += [0x00,0x12]                 # Sequence
        
        # ICMPv6 payload
        echoRequest    += [ord('a')+b for b in range(32)]
        
        # calculate ICMPv6 checksum
        pseudo  = []
        pseudo += echoRequest[24:40]                  # source address
        pseudo += echoRequest[8:24]                   # destination address
        pseudo += [0x00]*3+[len(echoRequest[40:])]    # upper-layer packet length
        pseudo += [0x00]*3                            # zero
        pseudo += [58]                                # next header
        pseudo += echoRequest[40:]                    # ICMPv6 header+payload
        
        crc     = checksum(pseudo)
        
        echoRequest[42]   = (crc&0x00ff)>>0
        echoRequest[43]   = (crc&0xff00)>>8
        
        return echoRequest
    
#============================ main ============================================

def main():
    
    #=== create eventBus client elements
    
    tunIf          = openTun.create()
    readThread     = ReadThread()
    writeThread    = WriteThread(readThread.dispatch)
    
    #=== wait for Enter to stop
    
    raw_input("Press enter to stop...\n")
    
    #=== stop eventBus client elements
    
    '''
    readThread.close()
    writeThread.close()
    tunIf.close()
    '''

if __name__ == '__main__':
    main()
