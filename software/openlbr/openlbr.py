#!/usr/bin/python

import binascii
import glob
import os
import serial
import signal
import struct
import sys
import threading
import time
import datetime
import socket
from fcntl import ioctl

#============================ parameters ================================================

import my_openprefix

IFF_TUN      = 0x0001
TUNSETIFF    = 0x400454ca

IPHC_TF_4B         = 0
IPHC_TF_3B         = 1
IPHC_TF_1B         = 2
IPHC_TF_ELIDED     = 3

IPHC_NH_INLINE     = 0
IPHC_NH_COMPRESSED = 1

IPHC_HLIM_INLINE   = 0
IPHC_HLIM_1        = 1
IPHC_HLIM_64       = 2
IPHC_HLIM_255      = 3 

IPHC_CID_NO        = 0
IPHC_CID_YES       = 1

IPHC_SAC_STATELESS = 0
IPHC_SAC_STATEFUL  = 1

IPHC_SAM_128B      = 0
IPHC_SAM_64B       = 1
IPHC_SAM_16B       = 2
IPHC_SAM_ELIDED    = 3

IPHC_M_NO          = 0
IPHC_M_YES         = 1

IPHC_DAC_STATELESS = 0
IPHC_DAC_STATEFUL  = 1

IPHC_DAM_128B      = 0
IPHC_DAM_64B       = 1
IPHC_DAM_16B       = 2
IPHC_DAM_ELIDED    = 3

#============================ variables =================================================

serialHandler      = ''
serialOutput       = ''
activateBridge     = False

serialOutputLock = threading.Lock()
#TODO using the Lock in a intelligent way

#============================ moteThread ================================================

class moteThread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
   def run(self):
      global serialHandler
      global activateBridge
      while True:
         global serialHandler
         availableports = scan()
         if (len(availableports)>0):
            try:
               serialHandler = serial.Serial(availableports[0],baudrate=115200,timeout=5)
            except:
               err = sys.exc_info()
               errorMessage = " ERROR [moteThread] 1: "+str(err[0])+" ("+str(err[1])+")"
               sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
               print errorMessage
            else:
               print "connected to "+serialHandler.portstr
               state = "WAIT_HEADER"
               numdelimiter = 0
               while True:
                  try:
                     char = serialHandler.read(1)
                  except SystemExit:
                     return
                  except:
                     err = sys.exc_info()
                     errorMessage = " ERROR [moteThread] 2: "+str(err[0])+" ("+str(err[1])+")"
                     sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
                     print errorMessage
                     break
                  else:
                     if (len(char)==0):
                        serialHandler.close()
                        break
                     if (state == "WAIT_HEADER"):
                        if char == '^':
                           numdelimiter = numdelimiter + 1
                        else:
                          numdelimiter = 0
                        if (numdelimiter==3):
                           state = "RECEIVING_COMMAND"
                           input = ""
                           numdelimiter = 0
                     else:
                        if (state == "RECEIVING_COMMAND"):
                           input=input+char
                           if char == '$':
                              numdelimiter = numdelimiter + 1
                           else:
                              numdelimiter = 0
                           if (numdelimiter==3):
                              state = "WAIT_HEADER"
                              numdelimiter = 0
                              input = input.rstrip('$')
                              try:
                                 parseInput(input)
                              except:
                                 err = sys.exc_info()
                                 errorMessage = " ERROR [moteThread] 3: "+str(err[0])+" ("+str(err[1])+")"
                                 sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
                                 print errorMessage
                                 pass
         else :
            errorMessage = " WARNING [moteThread]: no mote connected"
            sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
            print errorMessage
            time.sleep(1)

def scan():
   return glob.glob('/dev/ttyUSB*')

def parseInput(input):
   global serialHandler
   global activateBridge
   global serialOutput
   #byte 0 is the type of status message
   if (input[0]=="D"):
      print "========================= from mote ========================================"
      #input[0] is "D", input[1:2] is the addr_16b
      pkt_lowpan = input[3:]
      print_lowpan(pkt_lowpan)
      pkt_ipv6_disassembled = lowpan_to_ipv6(pkt_lowpan)
      print_ipv6(pkt_ipv6_disassembled)
      pkt_ipv6 = reassemble_ipv6_packet(pkt_ipv6_disassembled)
      pkt_ipv6 = chr(0)+chr(0)+chr(134)+chr(221)+pkt_ipv6
      os.write(f,pkt_ipv6)
   elif (input[0]=="R"):   #waiting for command
      if (ord(input[1])==200):  #input buffer empty
         serialOutputLock.acquire()
         if (len(serialOutput)>0):
            serialHandler.write('D')
            serialHandler.write(chr(len(serialOutput)))
            serialHandler.write(serialOutput)
            serialOutput = ''
         else:
            if activateBridge:
               serialHandler.write('B')
               serialHandler.write(chr(1+len(my_openprefix.IP64B_PREFIX)))
               serialHandler.write('Y')
               serialHandler.write(my_openprefix.IP64B_PREFIX)
               activateBridge = False
            else:
               serialHandler.write('R')
               serialHandler.write(chr(1))
               serialHandler.write('Y')
               activateBridge = True
         serialOutputLock.release()
   else:
      socketThreadHandler.send(input)

#============================ virtualInterfaceThread ====================================

class virtualInterfaceThread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
   def run(self):
      global serialOutput
      while True:
         #get IPv6 packet from tun interface
         data = os.read(f,1500)
         data = data[4:len(data)]
         #disassemble the IPv6 packet
         pkt = disassemble_ipv6_packet(data)
         print "========================= from virtual interface ==========================="
         print_ipv6(pkt) 
         #determine 64b nextHop address
         if (binascii.hexlify(pkt['dst_addr'])[0:2]=='ff'): #multicast address
            nextHop_string = 'ffffffffffffffff' #for IPv6 RAs
         else:
            nextHop_string = binascii.hexlify(pkt['dst_addr'])[16:33] #change this line when RPL will be implemented
         #encode nextHop
         nextHop = ''
         for i in range(0,8):
            nextHop += chr(int(nextHop_string[2*i:2*i+2],16))
         #compact IPv6 to 6LoWPAN
         pkt6s = ipv6_to_lowpan(pkt, IPHC_TF_ELIDED, IPHC_NH_INLINE, IPHC_HLIM_INLINE, \
                              IPHC_CID_NO, IPHC_SAC_STATELESS, IPHC_SAM_128B, IPHC_M_NO, \
                              IPHC_DAC_STATELESS, IPHC_DAM_128B)
         print_lowpan(pkt6s)
         if (len(pkt6s)>104): #because 104B data + 21B 15.4 header + 2B 15.4 footer = 127B
            errorMessage = " ERROR [virtualInterfaceThread] packet length= "+str(len(pkt6s))+" too long"
            sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
            print errorMessage
         else:
            #fill in serialOuput
            serialOutputLock.acquire()
            if (len(serialOutput)==0):
               serialOutput = nextHop + pkt6s
            serialOutputLock.release()

def output_wireshark(line):
   num_bytes_per_line = 16
   index=0
   for line_index in range(len(line)/num_bytes_per_line+1):
      chars = ''
      sys.stdout.write(openhex(index,6))
      while index<(line_index+1)*num_bytes_per_line and index<len(line):
         if ord(line[index])>32 and ord(line[index])<127:
            chars += line[index]
         else:
            chars += '.'
         sys.stdout.write(openhex(ord(line[index]),2))
         index += 1
      for i in range(index,(line_index+1)*num_bytes_per_line):
         sys.stdout.write('   ')
      sys.stdout.write(chars+'\n')

def openhex(num,length):
   output = ''
   for i in range(len((hex(num))[2:]),length):
      output += '0'
   output += (hex(num))[2:]+' '
   return output

# disassemble IPv6 packet into dictionnary with IPv6 header fields and payload
def disassemble_ipv6_packet(data):
   pkt = {};
   pkt['version']        = ord(data[0]) >> 4
   pkt['traffic_class']  = ((ord(data[0]) & 0x0F) << 4) + (ord(data[1]) >> 4)
   pkt['flow_label']     = ((ord(data[1]) & 0x0F) << 16) + (ord(data[2]) << 8) + ord(data[3])
   pkt['payload_length'] = (ord(data[4]) << 8) + ord(data[5])
   pkt['next_header']    = ord(data[6])
   pkt['hop_limit']      = ord(data[7])
   pkt['src_addr']       = data[8:8+16]
   pkt['dst_addr']       = data[24:24+16]
   pkt['payload']        = data[40:len(data)]
   return pkt

# reassemble an IPv6 packet previously disassembled
def reassemble_ipv6_packet(pkt):
   pktw = []
   pktw.append(chr((6 << 4) + (pkt['traffic_class'] >> 4)))
   pktw.append(chr( ((pkt['traffic_class'] & 0x0F) << 4) + (pkt['flow_label'] >> 16) ))
   pktw.append(chr( (pkt['flow_label'] >> 8) & 0x00FF ))
   pktw.append(chr( pkt['flow_label'] & 0x0000FF ))
   pktw.append(chr( pkt['payload_length'] >> 8 ))
   pktw.append(chr( pkt['payload_length'] & 0x00FF ))
   pktw.append(chr( pkt['next_header'] ))
   pktw.append(chr( pkt['hop_limit'] ))
   for i in range(0,16):
      pktw.append( pkt['src_addr'][i] )
   for i in range(0,16):
      pktw.append( pkt['dst_addr'][i] ) 
   pktws = ''.join(pktw)
   pktws = pktws + pkt['payload']
   return pktws

# print IPv6 packet (input: disassembled IPv6 packet)
def print_ipv6(pkt):
   print "--IPv6 packet--"
   print "Version:"       , pkt['version']
   print "Traffic class:" , pkt['traffic_class']
   print "Flow label:"    , pkt['flow_label']
   print "Payload length:", pkt['payload_length']
   print "Next header:"   , pkt['next_header']
   print "Hop limit:"     , pkt['hop_limit']
   print "Src address:"   , binascii.hexlify(pkt['src_addr'])
   print "Dst address:"   , binascii.hexlify(pkt['dst_addr'])
   print "Payload:"       , binascii.hexlify(pkt['payload'])
   pkt_reassembled = reassemble_ipv6_packet(pkt)
   output_wireshark(pkt_reassembled)

# print 6lowPAN packet
def print_lowpan(pkt6):
   print "--6LowPAN packet--"
   output_wireshark(pkt6)

#compact IPv6 header into 6LowPAN header (input: disassembled IPv6 packet; output: binary 6LoWPAN)
def ipv6_to_lowpan(pkt_ipv6, tf, nh, hlim, cid, sac, sam, m, dac, dam):
   # header
   pkt_lowpan = [];
   # Byte1: 011(3b) TF(2b) NH(1b) HLIM(2b)
   pkt_lowpan.append(chr((3 << 5) + (tf << 3) + (nh << 2) + (hlim << 0)))
   # Byte2: CID(1b) SAC(1b) SAM(2b) M(1b) DAC(2b) DAM(2b)
   pkt_lowpan.append(chr((cid << 7) + (sac << 6) + (sam << 4) + (m << 3) + (dac << 2) + (dam << 0)))
   # tf
   if (tf == IPHC_TF_3B):
      pkt_lowpan.append(chr((pkt_ipv6['flow_label'] & 0xff0000) >> 16))
      pkt_lowpan.append(chr((pkt_ipv6['flow_label'] & 0x00ff00) >> 8))
      pkt_lowpan.append(chr((pkt_ipv6['flow_label'] & 0x0000ff) >> 0))
   elif (tf == IPHC_TF_ELIDED):
      pass
   elif (tf == IPHC_TF_4B):
      errorMessage = " ERROR [ipv6_to_lowpan] unsupported tf==IPHC_TF_4B"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
      pass
   elif (tf == IPHC_TF_1B):
      errorMessage = " ERROR [ipv6_to_lowpan] unsupported tf==IPHC_TF_1B"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
      pass
   else:
      errorMessage = " ERROR [ipv6_to_lowpan] wrong tf=="+str(tf)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # nh
   if (nh == IPHC_NH_INLINE):
      pkt_lowpan.append(chr(pkt_ipv6['next_header']))
   elif (nh == IPHC_NH_COMPRESSED):
      errorMessage = " ERROR [ipv6_to_lowpan] unsupported nh==IPHC_NH_COMPRESSED"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
      pass
   else:
      errorMessage = " ERROR [ipv6_to_lowpan] wrong nh=="+str(nh)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # hlim
   if (hlim == IPHC_HLIM_INLINE):
      pkt_lowpan.append(chr(pkt_ipv6['hop_limit']))
   # IPHC_HLIM1,64,255 unsupported
   else:
      errorMessage = " ERROR [ipv6_to_lowpan] wrong hlim=="+str(hlim)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # sam
   if (sam == IPHC_SAM_ELIDED):
      pass
   elif (sam == IPHC_SAM_16B):
      for i in range(14,16):
         pkt_lowpan.append(pkt_ipv6['src_addr'][i])
   elif (sam == IPHC_SAM_64B):
      for i in range(8,16):
         pkt_lowpan.append(pkt_ipv6['src_addr'][i])
   elif (sam == IPHC_SAM_128B):
      for i in range(0,16):
         pkt_lowpan.append(pkt_ipv6['src_addr'][i])
   else:
      errorMessage = " ERROR [ipv6_to_lowpan] wrong sam=="+str(sam)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # dam
   if (dam == IPHC_DAM_ELIDED):
      pass
   elif (dam == IPHC_DAM_16B):
      for i in range(14,16):
         pkt_lowpan.append(pkt_ipv6['dst_addr'][i])
   elif (dam == IPHC_DAM_64B):
      for i in range(8,16):
         pkt_lowpan.append(pkt_ipv6['dst_addr'][i])
   elif (dam == IPHC_DAM_128B):
      for i in range(0,16):
         pkt_lowpan.append(pkt_ipv6['dst_addr'][i])
   else:
      errorMessage = " ERROR [ipv6_to_lowpan] wrong dam=="+str(dam)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # payload
   for i in range(0,len(pkt_ipv6['payload'])):
      pkt_lowpan.append(pkt_ipv6['payload'][i])
   # join
   pkt_lowpan = ''.join(pkt_lowpan)
   return pkt_lowpan

# inflate 6LoWPAN header into IPv6 header (input: binary 6LoWPAN; output: disassembled IPv6 packet)
def lowpan_to_ipv6(pkt_lowpan):
   pkt_ipv6 = dict()
   ptr = 2
   if ((ord(pkt_lowpan[0]) >> 5) != 0x003):
      errorMessage = " ERROR [lowpan_to_ipv6] not a 6LowPAN packet"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
      return   
   # tf
   tf = (ord(pkt_lowpan[0]) >> 3) & 0x03
   if (tf == IPHC_TF_3B):
      pkt_ipv6['flow_label'] = (ord(pkt_lowpan[ptr]) << 16) + (ord(pkt_lowpan[ptr+1]) << 8) + (ord(pkt_lowpan[ptr+2]) << 0)
      ptr = ptr + 3
   elif (tf == IPHC_TF_ELIDED):
      pkt_ipv6['flow_label'] = 0
   else:
      errorMessage = " ERROR [lowpan_to_ipv6] unsupported or wrong tf"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # nh
   nh = (ord(pkt_lowpan[0]) >> 2) & 0x01
   if (nh == IPHC_NH_INLINE):
      pkt_ipv6['next_header'] = ord(pkt_lowpan[ptr])
      ptr = ptr+1
   elif (nh == IPHC_NH_COMPRESSED):
      errorMessage = " ERROR [lowpan_to_ipv6] unsupported nh==IPHC_NH_COMPRESSED."
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
      pass
   else:
      errorMessage = " ERROR [lowpan_to_ipv6] wrong nh=="+str(nh)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # hlim
   hlim = ord(pkt_lowpan[0]) & 0x03
   if (hlim == IPHC_HLIM_INLINE):
      pkt_ipv6['hop_limit'] = ord(pkt_lowpan[ptr])
      ptr = ptr+1
   elif (hlim == IPHC_HLIM_1):
      pkt_ipv6['hop_limit'] = 1
   elif (hlim == IPHC_HLIM_64):
      pkt_ipv6['hop_limit'] = 64
   elif (hlim == IPHC_HLIM_255):
      pkt_ipv6['hop_limit'] = 255
   else:
      errorMessage = " ERROR [lowpan_to_ipv6] wrong hlim=="+str(hlim)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # sam
   sam = (ord(pkt_lowpan[1]) >> 4) & 0x03
   if (sam == IPHC_SAM_ELIDED):
      errorMessage = " ERROR [lowpan_to_ipv6] unsupported sam==IPHC_SAM_ELIDED"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   elif (sam == IPHC_SAM_16B):
      a1 = pkt_lowpan[ptr]
      a2 = pkt_lowpan[ptr+1]
      ptr = ptr+2
      s = ''.join(['\x00','\x00','\x00','\x00','\x00','\x00',a1,a2])
      pkt_ipv6['src_addr'] = my_openprefix.IP64B_PREFIX+s
   elif (sam == IPHC_SAM_64B):
      pkt_ipv6['src_addr'] = ''.join(my_openprefix.IP64B_PREFIX)+(pkt_lowpan[ptr:ptr+8])
      ptr = ptr + 8
   elif (sam == IPHC_SAM_128B):
      pkt_ipv6['src_addr'] = pkt_lowpan[ptr:ptr+16]
      ptr = ptr + 16
   else:
      errorMessage = " ERROR [lowpan_to_ipv6] wrong sam=="+str(sam)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # dam
   dam = (ord(pkt_lowpan[1]) & 0x03)
   if (dam == IPHC_DAM_ELIDED):
      errorMessage = " ERROR [lowpan_to_ipv6] unsupported dam==IPHC_DAM_ELIDED"
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   elif (dam == IPHC_DAM_16B):
      a1 = pkt_lowpan[ptr]
      a2 = pkt_lowpan[ptr+1]
      ptr = ptr+2
      s = ''.join(['\x00','\x00','\x00','\x00','\x00','\x00',a1,a2])
      pkt_ipv6['dst_addr'] = my_openprefix.IP64B_PREFIX+s
   elif (dam == IPHC_DAM_64B):
      pkt_ipv6['dst_addr'] = ''.join(my_openprefix.IP64B_PREFIX)+pkt_lowpan[ptr:ptr+8]
      ptr = ptr + 8
   elif (dam == IPHC_DAM_128B):
      pkt_ipv6['dst_addr'] = pkt_lowpan[ptr:ptr+16]
      ptr = ptr + 16
   else:
      errorMessage = " ERROR [lowpan_to_ipv6] wrong dam=="+str(dam)
      sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
      print errorMessage
   # payload
   pkt_ipv6['version']        = 6
   pkt_ipv6['traffic_class']  = 0
   pkt_ipv6['payload']        = pkt_lowpan[ptr:len(pkt_lowpan)]
   pkt_ipv6['payload_length'] = len(pkt_ipv6['payload'])
   return pkt_ipv6

#============================ socketThread ==============================================

class socketThread(threading.Thread):
   def __init__(self,socketport):
      print "opening socketThread on to port "+str(socketport)
      self.socket_handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket_handler.bind(('',socketport))
      self.conn = None
      threading.Thread.__init__(self)
   def run(self):
      global serialOutput
      self.socket_handler.listen(1)
      while True:
         self.conn,addr = self.socket_handler.accept()
         errorMessage = " STATUS [socketThread]: openVisualizer connection from "+addr[0]
         sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
         print errorMessage
         while True:
            try:
               networkInput = self.conn.recv(1024)
               serialOutputLock.acquire()
               if (len(serialOutput)==0):
                  serialOutput = networkInput
               serialOutputLock.release()
            except:
               err = sys.exc_info()
               errorMessage = " STATUS [socketThread]: OpenVisualizer closed? ("+str(err[0])+" "+str(err[1])+")"
               sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
               print errorMessage
               break
   def send(self,dataToSend):
      if self.conn:
         try:
            self.conn.send(dataToSend)
         except socket.error:
            self.conn = None
            print datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+': openVisualizer connection lost'
            pass

#============================ main ======================================================

# create virtual interface
print "\ncreating virtual interface..."
f = os.open("/dev/net/tun", os.O_RDWR)
ifs = ioctl(f, TUNSETIFF, struct.pack("16sH", "tun%d", IFF_TUN))
ifname = ifs[:16].strip("\x00")
print "done."

# configure IPv6 address
print "\nconfiguring IPv6 address..."
v = os.system('ifconfig ' + ifname + ' inet6 add ' + my_openprefix.IPV6PREFIX + '::1/64')
v = os.system('ifconfig ' + ifname + ' inet6 add fe80::1/64')
v = os.system('ifconfig ' + ifname + ' up')
print "done."

# set static route
print "\nsetting up static route..."
os.system('route -A inet6 add ' + my_openprefix.IPV6PREFIX + '::/64 dev ' + ifname)
print "done."

# enable IPv6 forwarding
print "\nenabling IPv6 forwarding..."
os.system('echo 1 > /proc/sys/net/ipv6/conf/all/forwarding')
print "done."

# start radvd
print "\nstarting radvd..."
os.system('radvd -C /etc/network/if-up.d/openlbr/my_openradvd.conf')
print "done."

print('\ncreated following virtual interface:')
os.system('ifconfig ' + ifname)

#declare threads
socketThreadHandler           = socketThread(8080)
moteThreadHandler             = moteThread()
virtualInterfaceThreadHandler = virtualInterfaceThread()

#start threads
socketThreadHandler.start()
moteThreadHandler.start()
virtualInterfaceThreadHandler.start()
