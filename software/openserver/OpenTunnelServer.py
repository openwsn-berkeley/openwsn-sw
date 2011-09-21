# this program listens to UDP port 'serverPort'. When it receives a packet, it creates
# a new IPv6 packet with the contents of the former. This allows non-IPv6 enables hosts
# to talk to IPv6 motes.

import socket, datetime, sys, time, threading

WKP_INTERNET_SIDE = 7788
WKP_MOTE_SIDE     = 8899

nat_table = {}

#============================ internetSideThread ==============================================

class internetSideThread(threading.Thread):
   def __init__(self):
      print "opening internetSideThread on to port "+str(WKP_INTERNET_SIDE)
      self.socket_handler = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.socket_handler.bind(('',WKP_INTERNET_SIDE))
      threading.Thread.__init__(self)
   def run(self):
      global moteSideThread_handler, nat_table
      while True:
         try:
            request,dist_addr = self.socket_handler.recvfrom(1024)
         except KeyboardInterrupt:
            print "\nInterrupted by user."
            self.socket_handler.close()
            time.sleep(1)
            sys.exit(0)
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error printError: %s (%s) \n" % (str(err[0]), str(err[1])))
            pass
         else:
            mote_ipv6_full         = request[0:32]
            i=0
            mote_ipv6 = ''
            while (i<len(mote_ipv6_full)):
               mote_ipv6 += mote_ipv6_full[i]
               if((i+1)%4==0 and i>0 and i<30):
                  mote_ipv6 += ':'
               i += 1
            mote_port             = int(request[32:36])
            udp_payload_to_send   = request[36:]
            nat_table[mote_ipv6_full,mote_port] = dist_addr
            output  = datetime.datetime.now().isoformat()
            output += " "+str(dist_addr[0])+"%"+str(dist_addr[1])
            output += " -> "+mote_ipv6+"%"+str(mote_port)
            print output
            moteSideThread_handler.sendto(udp_payload_to_send,mote_ipv6,mote_port)
   def sendto(self,udp_payload_to_send,dist_address):
      try:
         self.socket_handler.sendto(udp_payload_to_send,dist_address)
      except socket.error:
         return 0
      else:
         return 1

#============================ moteSideThread ==============================================

class moteSideThread(threading.Thread):
   def __init__(self):
      print "opening moteSideThread on to port "+str(WKP_MOTE_SIDE)
      self.socket_handler = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
      self.socket_handler.bind(('',WKP_MOTE_SIDE))
      threading.Thread.__init__(self)
   def run(self):
      global internetSideThread_handler, nat_table
      while True:
         try:
            request,dist_addr = self.socket_handler.recvfrom(1024)
         except KeyboardInterrupt:
            print "\nInterrupted by user."
            self.socket_handler.close()
            time.sleep(1)
            sys.exit(0)
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error printError: %s (%s) \n" % (str(err[0]), str(err[1])))
            pass
         else:
            mote_ipv6_full        = get_full_address(dist_addr[0])
            mote_port             = int(dist_addr[1])
            udp_payload_to_send   = request
            try:
               dist_addr = nat_table[mote_ipv6_full,mote_port]
            except:
               print "WARNING: no NAT entry for "+str(mote_ipv6_full)+"%"+str(mote_port)
            else:
               output  = datetime.datetime.now().isoformat()
               output += " "+str(mote_ipv6_full)+"%"+str(mote_port)
               output += " -> "+dist_addr[0]+"%"+str(dist_addr[1])
               print output
               internetSideThread_handler.sendto(udp_payload_to_send,dist_addr)
   def sendto(self,udp_payload_to_send,hisAddress,udp_destination_port):
      try:
         self.socket_handler.sendto(udp_payload_to_send,(hisAddress,udp_destination_port))
      except socket.error:
         return 0
      else:
         return 1

def get_full_address(temp_address):
   #disassemble IPv6 address in address_units
   address_blocks = temp_address.split('::')
   address_units = []
   for i in range(0,len(address_blocks)):
      address_units.append(address_blocks[i].split(':'))
      for j in range(0,len(address_units[i])):
         while (len(address_units[i][j])<4):
            address_units[i][j] = '0'+address_units[i][j]
   #reassemble IPv6 address as string
   full_connectionAddress  = ''
   if len(address_blocks)==1:
      for j in range(0,len(address_units[0])):
         full_connectionAddress += address_units[0][j]
   elif len(address_blocks)==2:
      for j in range(0,len(address_units[0])):
         full_connectionAddress += address_units[0][j]
      for j in range(0,8-len(address_units[0])-len(address_units[1])):
         full_connectionAddress += '0000'
      for j in range(0,len(address_units[1])):
         full_connectionAddress += address_units[1][j]
   #check if hex numbers only
   try:
      int(full_connectionAddress,16)
   except:
      full_connectionAddress  = ''
   return full_connectionAddress

#============================ main ======================================================

print "starting OpenTunnelServer.py..."

#declare threads
internetSideThread_handler = internetSideThread()
moteSideThread_handler     = moteSideThread()
#start threads
internetSideThread_handler.start()
moteSideThread_handler.start()
