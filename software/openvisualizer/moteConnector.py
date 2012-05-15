import threading
import socket
import openRecord

class moteConnector(threading.Thread):
   
   def __init__(self,(moteProbeIp,moteProbePort)):
      self.moteProbeIp   = moteProbeIp
      self.moteProbePort = moteProbePort
      self.socket        = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      print "creating moteConnector to connect to moteProbe@"+self.moteProbeIp+":"+str(self.moteProbePort)
      threading.Thread.__init__(self)
      self.setName('moteConnector to '+self.moteProbeIp+":"+str(self.moteProbePort))
   
   def run(self):
      while True:
         try:
            self.socket.connect((self.moteProbeIp,self.moteProbePort))
            while True:
               input = self.socket.recv(1024)
               openRecord.parseInput((self.moteProbeIp,self.moteProbePort),input)
         except socket.error:
            pass
   
   def write(self,stringToWrite):
      try:
         self.socket.send(stringToWrite)
      except socket.error:
         pass
