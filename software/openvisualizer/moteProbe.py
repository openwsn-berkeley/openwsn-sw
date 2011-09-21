import os
if os.name=='nt':       #windows
   import _winreg as winreg
elif os.name=='posix':  #linux
   import glob
import sys
import threading
import serial
import socket
import datetime
import time
import binascii

def findSerialPortsNames():
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

class moteProbe():
   def __init__(self,serialport,socketport):
      self.serialport = serialport
      self.socketport = socketport
      print "creating moteProbe attaching to "+self.serialport+", listening to TCP port "+str(self.socketport)
      # declare serial and socket threads
      self.serialThread = moteProbeSerial(self.serialport)
      self.socketThread = moteProbeSocket(self.socketport)
      # inform one of another
      self.serialThread.setOtherThreadHandler(self.socketThread)
      self.socketThread.setOtherThreadHandler(self.serialThread)
      # start threads
      self.serialThread.start()
      self.socketThread.start()

class moteProbeSerial(threading.Thread):

   def __init__(self,serialport):
      self.serialport        = serialport
      self.serialInput       = ''
      self.serialOutput      = ''
      self.serialOutputLock  = threading.Lock()
      self.state             = 'WAIT_HEADER'
      self.numdelimiter      = 0
      threading.Thread.__init__(self)
      self.setName('moteProbeSerial@'+self.serialport)
      
   def setOtherThreadHandler(self,otherThreadHandler):
      self.otherThreadHandler = otherThreadHandler
   
   def run(self):
      while True:    # open serial port
         self.serial = serial.Serial(self.serialport,baudrate=115200)
         while True: # read bytes from serial port
            try:
               char = self.serial.read(1)
            except:
               err = sys.exc_info()
               sys.stderr.write( "ERROR moteProbeSerial: %s (%s) \n" % (str(err[0]), str(err[1])))
               time.sleep(1)
               break
            else:
               if    self.state == 'WAIT_HEADER':
                  if char == '^':
                     self.numdelimiter     += 1
                  else:
                     self.numdelimiter      = 0
                  if self.numdelimiter==3:
                     self.state             = 'RECEIVING_COMMAND'
                     self.serialInput       = ''
                     self.numdelimiter      = 0
               elif self.state == 'RECEIVING_COMMAND':
                  self.serialInput = self.serialInput+char
                  if char == '$':
                     self.numdelimiter     += 1
                  else:
                     self.numdelimiter      = 0
                  if self.numdelimiter==3:
                     self.state             = 'WAIT_HEADER'
                     self.numdelimiter      = 0
                     self.serialInput       = self.serialInput.rstrip('$')
                     #byte 0 is the type of status message
                     if self.serialInput[0]=="R":     #request for data
                        if (ord(self.serialInput[1])==200):  # byte 1 indicates free space in mote's input buffer
                           self.serialOutputLock.acquire()
                           self.serial.write(self.serialOutput)
                           self.serialOutput = ''
                           self.serialOutputLock.release()
                     else:
                        # send to other thread
                        self.otherThreadHandler.send(self.serialInput)
               else:
                  print 'ERROR [moteProbeSerial]: invalid state='+state
                              
   def send(self,bytesToSend):
      self.serialOutputLock.acquire()
      self.serialOutput += 'D'+ chr(len(self.serialOutput)) + bytesToSend
      if len(self.serialOutput)>200:
         print 'WARNING [moteProbeSerial@'+self.serialport+'] serialOutput overflowing ('+str(len(self.serialOutput))+' bytes)'
      self.serialOutputLock.release()
                                 
class moteProbeSocket(threading.Thread):

   def __init__(self,socketport):
      self.socketport        = socketport
      self.socket            = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.conn              =  None
      threading.Thread.__init__(self)
      self.setName('moteProbeSocket@'+str(self.socketport))
      
   def setOtherThreadHandler(self,otherThreadHandler):
      self.otherThreadHandler = otherThreadHandler
   
   def run(self):
      self.socket.bind(('',self.socketport)) # attach to a socket on whatever IPv4 address of the computer
      self.socket.listen(1)                  # listen for incoming connection requests from the OpenVisualizer
      while True:
         # wait for OpenVisualizer to connect
         self.conn,self.addr = self.socket.accept()
         # record that I'm connected now
         print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+': openVisualizer connection from '+str(self.addr)
         # read data sent from OpenVisualizer
         while True:
            try:
               bytesReceived = self.conn.recv(4096)
               self.otherThreadHandler.send(bytesReceived)
            except socket.error:
               print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+': openVisualizer disconnected'
               self.conn = None
               break
   
   def send(self,bytesToSend):
      if self.conn!=None:
         try:
            self.conn.send(bytesToSend)
         except socket.error:
            # happens when not connected
            pass

'''
if this module is run by itself (i.e. not imported from OpenVisualizer),
it has to create moteProbe threads for each mote connected
'''
if __name__ == '__main__':
   print 'moteProbe run as a standalone application'
   serialPortNames     = findSerialPortsNames()
   port_number         = 8080
   for serialPortName in serialPortNames:
      moteProbe(serialPortName,port_number)
      port_number += 1