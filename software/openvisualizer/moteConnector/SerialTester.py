import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SerialTester')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading
import socket
import random

class SerialTester(threading.Thread):
    
    DFLT_TESTPKT_LENGTH = 10  ##< number of bytes in a test packet
    DFLT_NUM_TESTPKT    = 20  ##< number of test packets to send
    DFLT_TIMEOUT        = 5   ##< timeout in second for getting a reply
    
    def __init__(self,moteProbeIp,moteProbeTcpPort):
        
        # log
        log.debug("creating instance")
        
        # store params
        self.moteProbeIp          = moteProbeIp
        self.moteProbeTcpPort     = moteProbeTcpPort
        
        # local variables
        self.dataLock             = threading.RLock()
        self.socket               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.goOn                 = True
        self.testPktLen           = self.DFLT_TESTPKT_LENGTH
        self.numTestPkt           = self.DFLT_NUM_TESTPKT
        self.timeout              = self.DFLT_TIMEOUT
        self.traceCb              = None
        self.busyTesting          = False
        self.lastSent             = []
        self.lastReceived         = []
        self.waitForReply         = threading.Event()
        self._resetStats()
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name = 'SerialTester@{0}:{1}'.format(self.moteProbeIp,self.moteProbeTcpPort)
        
    def run(self):
        # log
        log.debug("starting to run")
        
        while self.goOn:
            try:
                # connect
                self.socket.connect((self.moteProbeIp,self.moteProbeTcpPort))
                log.debug("connecting to moteProbe@{0}:{1}".format(self.moteProbeIp,self.moteProbeTcpPort))
                
                while True:
                    
                    # retrieve the string of bytes from the socket
                    inputString        = self.socket.recv(1024)
                    input              = [ord(c) for c in inputString]
                    
                    # handle input
                    if (chr(input[0])=='D'):
                        
                        # don't handle if I'm not testing
                        with self.dataLock:
                            if not self.busyTesting:
                                continue
                        
                        with self.dataLock:
                            # record what I just received
                            self.lastReceived = input[1+2+5:] # 'H' (1), moteId (2), ASN (5)
                            
                            # wake up other thread
                            self.waitForReply.set()
                    
            except socket.error as err:
                log.error(err)
                pass
    
    def quit(self):
        self.goOn = False
        self.socket.close()
    
    #======================== public ==========================================
    
    #===== setup test
    
    def setTestPktLength(self,newLength):
        with self.dataLock:
            self.testPktLen  = newLength
    
    def setNumTestPkt(self,newNum):
        with self.dataLock:
            self.numTestPkt  = newNum
    
    def setTimeout(self,newTimeout):
        with self.dataLock:
            self.timeout     = newTimeout
    
    def setTrace(self,newTraceCb):
        with self.dataLock:
            self.traceCb     = newTraceCb
    
    #===== run test
    
    def test(self,blocking=True):
        if blocking:
            self._runtest()
        else:
            threading.Thread(target=self._runtest).start()
    
    #===== get test results
    
    def getStats(self):
        returnVal = None
        with self.dataLock:
            returnVal = self.stats.copy()
        return returnVal
    
    #======================== private =========================================
    
    def _runtest(self):
        
        # I'm testing
        with self.dataLock:
            self.busyTesting = True
            
        # gather test parameters
        with self.dataLock:
            testPktLen = self.testPktLen
            numTestPkt = self.numTestPkt
            timeout    = self.timeout
        
        # reset stats
        self._resetStats()
        
        # send packets and collect stats
        for i in range(numTestPkt):
            
            # prepare random packet to send
            packetToSend = [random.randint(0x00,0xff) for _ in range(testPktLen)]
            
            # remember as last sent packet
            with self.dataLock:
                self.lastSent = packetToSend[:]
            
            # send
            self.socket.send(''.join(['H']+[chr(b) for b in packetToSend]))
            with self.dataLock:
                self.stats['numSent']                 += 1
            
            # log
            self._log('\nsent:     {0}'.format(self.formatList(self.lastSent)))
            
            # wait for answer
            self.waitForReply.clear()
            if self.waitForReply.wait(timeout):
                
                # log
                self._log('received: {0}'.format(self.formatList(self.lastReceived)))
                
                # echo received
                with self.dataLock:
                    if self.lastReceived==self.lastSent:
                        self.stats['numOk']           += 1
                    else:
                        self.stats['numCorrupted']    += 1
                        self._log('!! corrupted.')
            else:
                # timeout
                with self.dataLock:
                    self.stats['numTimeout']          += 1
                    self._log('!! timeout.')
        
        # I'm not testing
        with self.dataLock:
            self.busyTesting = False
    
    def _log(self,msg):
        log.debug(msg)
        with self.dataLock:
            if self.traceCb:
                self.traceCb(msg)
    
    def _resetStats(self):
        with self.dataLock:
            self.stats                = {
                'numSent'             : 0,
                'numOk'               : 0,
                'numCorrupted'        : 0,
                'numTimeout'          : 0,
            }
    
    def formatList(self,l):
        return '-'.join(['%02x'%b for b in l])