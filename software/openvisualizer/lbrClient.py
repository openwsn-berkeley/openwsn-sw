import os
import sys
import shared
import threading
import serial
import socket
import datetime
import time
import errno
import binascii
import Tkinter
import tkFileDialog
import tkMessageBox
import re

AUTHTIMEOUT = 5.0 # max number of seconds to wait for an authentication packet

class lbrClientThread(threading.Thread):
   
   def __init__(self,frame,tkSem):
      print "creating lbrClientThread"
      self.varLock           = threading.BoundedSemaphore()
      self.isConnected       = False
      self.connectSem        = threading.BoundedSemaphore()
      self.connectSem.acquire()
      self.tkSem             = tkSem
      self.frame             = frame
      self.tkSem.acquire()
      self.lbrPrefixLabel    = Tkinter.Label(self.frame,width=20)
      self.lbrPrefixLabel.grid(row=0,column=0,columnspan=2)
      Tkinter.Label(self.frame,text='status:',justify=Tkinter.RIGHT,anchor=Tkinter.E).grid(row=1,column=0)
      self.lbrStatusLabel    = Tkinter.Label(self.frame)
      self.lbrStatusLabel.grid(row=1,column=1)
      Tkinter.Label(self.frame,text='sent to LBR:',justify=Tkinter.RIGHT,anchor=Tkinter.E).grid(row=2,column=0)
      self.lbrSentLabel      = Tkinter.Label(self.frame)
      self.lbrSentLabel.grid(row=2,column=1)
      Tkinter.Label(self.frame,text='received from LBR:',justify=Tkinter.RIGHT,anchor=Tkinter.E).grid(row=3,column=0)
      self.lbrReceivedLabel  = Tkinter.Label(self.frame)
      self.lbrReceivedLabel.grid(row=3,column=1)
      self.connectButton     = Tkinter.Button(self.frame,text="Connect to LBR",command=self.connect)
      self.connectButton.grid(row=4,column=0,columnspan=2)
      self.tkSem.release()
      self.sentColor         = 'red'
      self.receivedColor     = 'red'
      threading.Thread.__init__(self)
      self.setName('lbrClientThread')
   
   def run(self):
      while True:
         self.resetStats()
         self.displayStats()
         self.connectSem.acquire()
         self.connectSem.release()
         try:
            while True:
               input = self.socket.recv(4096)
               if not input:
                  self.varLock.acquire()
                  tempConnected = self.isConnected
                  self.varLock.release()
                  if tempConnected == True:
                     self.disconnect()
                  break
               #update statistics
               self.receivedPackets += 1
               self.receivedBytes   += len(input)
               self.displayStats()
               # handle received data
               # the data received from the LBR should be:
               # - first 8 bytes: EUI64 of the final destination
               # - remainder: 6LoWPAN packet and above
               if len(input)<8:
                  print '[lbrClient] ERROR: received packet from LBR which is too short ('+str(len(input))+' bytes)'
                  print binascii.hexlify(input)
                  continue
               # look for the connected mote which is a bridge
               if shared.portBridgeMote!=None:
                  shared.moteConnectors[shared.portBridgeMote].write(input)
               else:
                  if self.receivedColor=='red':
                     self.receivedColor = 'orange'
                  else:
                     self.receivedColor = 'red'
                  self.tkSem.acquire()
                  self.lbrReceivedLabel.config(background=self.receivedColor)
                  self.tkSem.release()
         except socket.error:
            print 'poipoipoipoi'
            self.disconnect()
   
   def resetStats(self):
      self.prefix          = ''
      self.status          = 'disconnected'
      self.sentPackets     = 0
      self.sentBytes       = 0
      self.receivedPackets = 0
      self.receivedBytes   = 0
   
   def displayStats(self):
      self.tkSem.acquire()
      self.lbrPrefixLabel.config(text=self.prefix)
      self.lbrStatusLabel.config(text=self.status)
      tempString  =      str(self.sentPackets)+' pkts'
      tempString += ', '+str(self.sentBytes)  +' B '
      if self.sentPackets!=0:
         tempString += ' ('+str(self.sentBytes/self.sentPackets)+' B/pkt ) '
      self.lbrSentLabel.config(text=tempString)
      tempString  =      str(self.receivedPackets)+' pkts'
      tempString += ', '+str(self.receivedBytes)  +' B '
      if self.receivedPackets!=0:
         tempString += ' ('+str(self.receivedBytes/self.receivedPackets)+'B/pkt) '
      self.lbrReceivedLabel.config(text=tempString)
      self.tkSem.release()
   
   def connect(self):
      # open authentication file
      authFile = tkFileDialog.askopenfile(mode='r',
                                          title = 'Select an LBR authentication file',
                                          multiple = False,
                                          initialfile = 'guest.lbrauth',
                                          filetypes = [("LBR authentication file", "*.lbrauth")] )
      # parse authentication file
      try:
         for line in authFile:
            match = re.search('(.*)=(.*)',line)
            if match!=None:
               key = match.group(1).strip()
               val = match.group(2).strip()
               if   key=='LBRADDR':
                  self.lbrAddr = val
               elif key=='LBRPORT':
                  self.lbrPort = int(val)
               elif key=='NETNAME':
                  self.netname = val
         self.lbrAddr # this line makes sure this variable exists
         self.lbrPort # this line makes sure this variable exists
         self.netname # this line makes sure this variable exists
      except:
         tkMessageBox.showerror('Error','Misformed LBR authentication file.')
         return
      # update stats
      self.status          = 'connecting'
      self.displayStats()
      # create TCP socket to connect to LBR
      try:
         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.socket.connect((self.lbrAddr,self.lbrPort))
      except:
         try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
         except socket.error:
            pass
         tkMessageBox.showerror('Error','Could not open socket to LBR@'+self.lbrAddr+':'+str(self.lbrPort))
         return
      # update stats
      self.status          = 'authenticating'
      self.displayStats()
      self.socket.settimeout(AUTHTIMEOUT) # listen for at most AUTHTIMEOUT seconds
      # ---S---> send security capability
      self.socket.send('S'+chr(0))
      # <---S--- listen for (same) security capability
      try:
         input = self.socket.recv(4096)
      except socket.timeout:
         try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
         except socket.error:
            pass
         tkMessageBox.showerror('Error','Waited too long for security reply')
         return
      if (len(input)!=2   or
          input[0]  !='S' or
          input[1]  !=chr(0)):
         try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
         except socket.error:
            pass
         tkMessageBox.showerror('Error','Incorrect security reply from LBR')
         return
      # ---N---> send netname
      self.socket.send('N'+self.netname)
      try:
         input = self.socket.recv(4096)
      except socket.timeout:
         try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
         except socket.error:
            pass
         tkMessageBox.showerror('Error','Waited too long for netname')
         return
      # <---P--- listen for prefix
      try:
         input = self.socket.recv(4096)
      except socket.timeout:
         try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
         except socket.error:
            pass
         tkMessageBox.showerror('Error','Waited too long for prefix')
         return
      if (len(input)!=20 or
          input[0]!='P'):
         try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
         except socket.error:
            pass
         tkMessageBox.showerror('Error','Invalid prefix information from LBR')
         return
      self.socket.settimeout(None) # no socket timeout from now on
      self.prefix = input[1:]
      # update GUI elements
      self.prefix = self.prefix
      self.status = 'connected to LBR@'+self.lbrAddr+':'+str(self.lbrPort)
      self.displayStats()
      self.tkSem.acquire()
      self.connectButton.configure(text="Disconnect from LBR")
      self.connectButton.configure(command=self.disconnect)
      self.tkSem.release()
      # release semaphore so task can start running
      self.varLock.acquire()
      self.isConnected = True
      self.varLock.release()
      self.connectSem.release()
   
   def disconnect(self):
      self.connectSem.acquire()
      # 
      self.varLock.acquire()
      self.isConnected = False
      self.varLock.release()
      # close the TCP session
      self.socket.shutdown(socket.SHUT_RDWR)
      self.socket.close()
      # update GUI elements
      self.resetStats()
      self.displayStats()
      self.connectButton.configure(text="Connect to LBR")
      self.connectButton.configure(command=self.connect)
   
   def send(self,lowpan):
      p = ""
      count = 0
      while (count < 16):
         p = p + str(int(binascii.b2a_hex(lowpan)[108 + count * 4 : 112 + count * 4],16)) + ","
         count = count + 1
      print p
      f = open('C:/Users/David/test.txt', 'a')
      f.write(p + "\n")

      #print str(int(binascii.b2a_hex(lowpan)[108:112],16)) + "," + str(int(binascii.b2a_hex(lowpan)[112:116],16))
      # print lowpan

      self.varLock.acquire()
      tempIsConnected = self.isConnected
      self.varLock.release()
      try:
         if tempIsConnected==True:
            self.tkSem.acquire()
            self.lbrSentLabel.config(background='green')
            self.tkSem.release()
            self.socket.send(chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+chr(0)+lowpan)
            self.sentPackets += 1
            self.sentBytes   += len(lowpan)+8
            self.displayStats()
         else:
            if self.sentColor=='red':
               self.sentColor = 'orange'
            else:
               self.sentColor = 'red'
            self.tkSem.acquire()
            self.lbrSentLabel.config(background=self.sentColor)
            self.tkSem.release()
      except socket.error:
         print 'ERROR: socket error while sending'
         pass
