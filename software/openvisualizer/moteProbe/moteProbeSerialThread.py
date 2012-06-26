import threading
import serial

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('moteProbeSerialThread')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class moteProbeSerialThread(threading.Thread):

    def __init__(self,serialport):
        
        # log
        log.debug("create instance")
        
        # store params
        self.serialport           = serialport
        
        # local variables
        self.serialInput          = ''
        self.serialOutput         = ''
        self.serialOutputLock     = threading.Lock()
        self.state                = 'HDLC_DONE_RECEIVING'
		self.isStuffing           = False
        self.numdelimiter         = 0
		self.crc                  = 0
		self.fcs                  = 0 #crc is the one I get from the packet and fcs is the one I compute here
        
        # initialize the parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'moteProbeSerialThread@'+self.serialport
    
    def run(self):
        
        # log
        log.debug("start running")
    
        while True:     # open serial port
            log.debug("open serial port")
            self.serial = serial.Serial(self.serialport,baudrate=115200)
            while True: # read bytes from serial port
                try:
                    char = self.serial.read(1)
                except Exception as err:
                    log.warning(err)
                    time.sleep(1)
                    break
                else:
					if char == chr(0x7e):
                        self.numdelimiter     += 1
							
                    else:
                        self.numdelimiter      = 0
                    if (self.numdelimiter==1 and self.state == 'HDLC_DONE_RECEIVING'): #means we're just starting
                        self.state             = 'HDLC_RECEIVING'
                        self.serialInput       = ''
                        self.numdelimiter      = 0
                    elif (self.numdelimiter==0 and self.state == 'HDLC_RECEIVING'):
						if (self.isStuffing ==True and char==chr(0x5e)):#0x5e
							self.serialInput = self.serialInput+chr(0x7e)
						elif (self.isStuffing ==True and char==chr(0x5d)):#0x5d
							#do nothing; ignore this byte
						else:
							self.serialInput = self.serialInput+char
					elif (self.numdelimiter==1 and  self.state == 'HDLC_RECEIVING'):#means we're done
						self.state             = 'HDLC_DONE_RECEIVING'
						#NOW DO THE CRC AND CALLBACK
						fcs_calc(self,self.serialInput)
						self.crc = self.serialInput[len(self.serialInput)-2] + (self.serialInput[len(self.serialInput)-1]<<8)
						if self.crc == self.fcs:
							self.serialInput = self.serialInput[0:-2]#remove the crc bytes
							print(self.serialInput) #here do the appropriate action
						else
							#complain about bad crc
							print('bad crc')
						
					#the next lines are for stuffing on the fly
					if(char == chr(0x7d)):#0x7d
						self.isStuffing = True
					else:
						self.isStuffing = False

    #======================== public ==========================================
    
    def setOtherThreadHandler(self,otherThreadHandler):
        self.otherThreadHandler = otherThreadHandler
    
    def send(self,bytesToSend):
        self.serialOutputLock.acquire()
        hdlcify(self,bytesToSend)
		self.serialOutput = bytesToSend
        if len(self.serialOutput)>200:
            log.warning("serialOutput overflowing ({0} bytes)".format(len(self.serialOutput)))
        self.serialOutputLock.release()
    
    #======================== private =========================================
	def fcs_calc(self,packet):
		self.fcs = 65535 #0xffff
		for count in range(len(packet)-2):
			self.fcs=fcs_fcs16(self,packet[count])
		self.fcs = ~self.fcs #one's complement
			
			
	def fcs_fcs16(self,char):
		v = (self.fcs ^ char) & 255;
		for i in range(8):
			v = ((v>>1)^0x8408) if (v&1) else (v>>1) #should it be v&&1??????
		v = (self.fcs>>8)^v
		return v
		
	def hdlcify(self,bytes):
		#adding the frame check sequence
		fcs_calc(self,bytes)
		bytes = bytes + chr(self.fcs&0x00ff) + chr(self.fcs>>8)
		#perform the stuffing
		newbytes=''
		counter = 0
		for c in range(len(bytes)):
			if bytes[counter]==chr(0x7e): #stuffing 7e
				newbytes[counter]=chr(0x7d)
				newbytes[counter+1]=chr(0x5e)
				counter+=2
			elif bytes[counter]==chr(0x7d): #stuffing 7d
				newbytes[counter]=chr(0x7d)
				newbytes[counter+1]=chr(0x5d)
				counter+=2
			else:
				newbytes[counter] = bytes[counter]
				counter+=1
				
		bytes = '~' + newbytes + '~' #add the first and last 7e