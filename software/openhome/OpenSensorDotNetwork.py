import socket, datetime, sys

apiKey            = "DqApznQuoaayVuVtIunc8oM1UXCPDMNiQdf+eqjvLmo="
myAddress         = '' #means 'all'
myPort            = 8080

# creates a datastream
#
# @param sensornodeId the identifier of a mote
# @param sensorType the type of sensor ("humidity", "temperature", "lightir", "lightvisible")
#
# @return httpReturnCode
#   201 succesfully created
#   303 datastream already exists
#   400 malformed request
#   401 authentication error
# @return datastreamId identifier of the datastream (int), or 0 if error 4**
#
def create_datastream(sensornodeId, sensorType):
   datastreamName = "OpenWSN_mote_"+str(sensornodeId)+"_"+sensorType

   httpBody       = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
   httpBody      += "<datastream>\n"
   httpBody      += "<name>"+datastreamName+"</name>\n"
   httpBody      += "<category>unknown</category>\n"
   httpBody      += "<permissions>100663300</permissions>\n"
   httpBody      += "<value>\n"
   httpBody      += "<name>"+sensorType+"</name>\n"
   httpBody      += "<type>int</type>\n"
   httpBody      += "<units>units</units>\n"
   httpBody      += "</value>\n"
   httpBody      += "</datastream>\n"

   httpHeader     = "POST /rest/resources/datastreams HTTP/1.1\n"
   httpHeader    += "Host: incoherent.sunlabs.com\n"
   httpHeader    += "X-SensorNetworkAPIKey:"+apiKey+"\n"
   httpHeader    += "Content-type: application/xml\n"
   httpHeader    += "Content-Length: "+str(len(httpBody))+"\n"
   httpHeader    += "\n"

   httpRequest    = httpHeader + httpBody

   try:
      res = socket.getaddrinfo('incoherent.sunlabs.com', 80, socket.AF_INET, socket.SOCK_STREAM)
      af, socktype, proto, canonname, sa = res[0]
      
      socket_handler = socket.socket(af, socktype, proto)
      socket_handler.connect(sa)
      socket_handler.send(httpRequest)

      httpReply = socket_handler.recv(1024)
   except:
      err = sys.exc_info()
      errorMessage = " ERROR create_datastream: "+str(err[0])+" ("+str(err[1])+")"
      sys.stderr.write("\n"+datetime.datetime.now().isoformat()+errorMessage+'\n')
      return 'error',0

   httpReturnCode = int((httpReply.split('\r\n'))[0].split(' ')[1])
   try:
      temp = (httpReply.split('\r\n')[3]).split('/')
      datastreamId = int(temp[len(temp)-1])
   except:
      datastreamId = 0

   return httpReturnCode,datastreamId


# insert data into a datastream. If the datastream does not exist, create it first
#
# @param sensornodeId the identifier of a mote
# @param sensorType the type of sensor ("humidity", "temperature", "lightir", "lightvisible")
# @param sensorValue
#
# @return httpReturnCode
#   200 data successfully inserted
#   400 malformed request
#   401 authentication error
#   404 datastream does not exist
# @return datastreamId identifier of the datastream (int), or 0 if error 4**
#
def insert(sensornodeId, sensorType, sensorValue):

   httpReturnCode,datastreamId = create_datastream(sensornodeId,sensorType)
   if (httpReturnCode==400 or httpReturnCode==404 or httpReturnCode=='error'):
      return 'error'

   httpBody       = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
   httpBody      += "<sampleData>\n"
   httpBody      += "<sensorNodeId>"+str(sensornodeId)+"</sensorNodeId>\n"
   httpBody      += "<timestamp>"+datetime.datetime.now().isoformat()+"</timestamp>\n"
   httpBody      += "<value>"+str(sensorValue)+"</value>\n"
   httpBody      += "</sampleData>\n"

   httpHeader     = "POST /rest/resources/datastreams/"+str(datastreamId)+"/data HTTP/1.1\n"
   httpHeader    += "Host: incoherent.sunlabs.com\n"
   httpHeader    += "X-SensorNetworkAPIKey:"+apiKey+"\n"
   httpHeader    += "Content-type: application/xml\n"
   httpHeader    += "Content-Length: "+str(len(httpBody))+"\n"
   httpHeader    += "\n"

   httpRequest    = httpHeader + httpBody

   try:
      res = socket.getaddrinfo('incoherent.sunlabs.com', 80, socket.AF_INET, socket.SOCK_STREAM)
      af, socktype, proto, canonname, sa = res[0]

      socket_handler = socket.socket(af, socktype, proto)
      socket_handler.connect(sa)
      socket_handler.send(httpRequest)

      httpReply = socket_handler.recv(1024)
   except:
      err = sys.exc_info()
      errorMessage = " ERROR insert: "+str(err[0])+" ("+str(err[1])+")"
      sys.stderr.write("\n"+datetime.datetime.now().isoformat()+errorMessage+'\n')
      return 'error'

   httpReturnCode = int((httpReply.split('\r\n'))[0].split(' ')[1])
   return httpReturnCode

#============================ main ======================================================

print "starting OpenSensorDotNetwork..."

socket_handler = socket.socket(socket.AF_INET6,socket.SOCK_DGRAM)
socket_handler.bind((myAddress,myPort))
while True:
   try:
      request,dist_addr = socket_handler.recvfrom(1024)
   except KeyboardInterrupt:
      print "\nInterrupted by user."
      sys.exit(0)
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error printError: %s (%s) \n" % (str(err[0]), str(err[1])))
      pass
   else:
      #extract sensornodeId
      temp = str(dist_addr[0])
      temp = temp.split(':')
      sensornodeId = temp[len(temp)-1]
      #extract sensorType
      if   request[0]=='H':
        sensorType     = "humidity"
      elif request[0]=='T':
        sensorType     = "temperature"
      elif request[0]=='I':
        sensorType     = "lightir"
      elif request[0]=='V':
        sensorType     = "lightvisible"
      elif request[0]=='L':
        sensorType     = "lollipop"
      else:
        print 'ERROR sensorType unknown'
        pass
      #extract sensorValue
      try:
        sensorValue = int(ord(request[2])) + int(ord(request[3]))*256
      except:
        print 'ERROR sensorValue unknown'
        pass
      #send to incoherent.sunlabs.com
      httpReturnCode = insert(sensornodeId,sensorType,sensorValue)
      output  = datetime.datetime.now().isoformat()
      output += " "+str(dist_addr[0])+"%"+str(dist_addr[1])+" -> "+myAddress+"%"+str(myPort)
      output += " "+sensorType+" ("+str(len(request))+" bytes)"
      output += " (httpReturnCode="+str(httpReturnCode)+")"
      print output
socket_handler.close()
