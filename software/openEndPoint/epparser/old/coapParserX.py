import binascii
import socket
import struct
import os
import datetime

port = 5683

option_codes = {
  #response codes
  65:"2.01 Created",
  66:"2.02 Deleted",
  67:"2.03 Valid",
  68:"2.04 Changed",
  69:"2.05 Content",
 128:"4.00 Bad Request ",
 129:"4.01 Unauthorized",
 130:"4.02 Bad Option",
 131:"4.03 Forbidden",
 132:"4.04 Not Found",
 133:"4.05 Method Not Allowed",
 140:"4.12 Precondition Failed",
 141:"4.13 Request Entity Too Large",
 143:"4.15 Unsupported Media Type",
 160:"5.00 Internal Server Error",
 161:"5.01 Not Implemented",
 162:"5.02 Bad Gateway",
 163:"5.03 Service Unavailable ",
 164:"5.04 Gateway Timeout",
 165:"5.05 Proxying Not Supported",
 #option number registry
 1:"Content-Type",
 2:"Max-Age",
 3:"Proxy-Uri",
 4:"ETag",
 5:"Uri-Host",
 6:"Location-Path",
 7:"Uri-Port",
 8:"Location-Query",
 9:"Uri-Path",
 11:"Token",
 12:"Accept",
 13:"If-Match",
 15:"Uri-Query",
 21:"If-None-Match",
 #media types
 0:"text/plain; charset=utf-8",
 40:"application/link-format",
 41:"application/xml",
 42:"application/octet-stream",
 47:"application/exi",
 50:"application/json"
}
                  

def parseCoapData(data, address):
   #try:
        version = int((ord(data[0])& 0xc0) >> 6)
        type = int((ord(data[0])& 0x30) >> 4)
        options = int((ord(data[0])& 0xF))
        code = int(ord(data[1]))
        #for now we only deal with code=3(PUT) code=2(POST)
        mId = int(str(data[2:4]).encode("hex"),16)
        optionList = []
        option_pointer = 4
        #print version,type,options,code
	for i in range(0, options):
            optionDelta = int((ord(data[option_pointer])&0b11110000)>>4)
            optionNumber = optionDelta
            if i > 0:
               optionNumber = optionDelta + optionList[i-1][0]
            length = int(ord(data[option_pointer])&0b00001111)
            print data[option_pointer+1:option_pointer+length+1]
	    option_payload = data[option_pointer+1:option_pointer+length+1]
            option_desc = "" #string describing option
	    try:
               #try to get a string to associate with the option code, if none exists use the number
                #option_payload = int(ord(option_payload))
		#option_payload = option_codes[optionDelta]
            	option_desc = option_codes[optionNumber]
	    except:
               pass
            optionList.append([optionDelta, length, option_desc, option_payload])
            option_pointer = option_pointer + length + 1

        #print "poipoi start"
        #for b in data[option_pointer:option_pointer+5]:
            #print str(ord(b))
        #xaviPayload = 256*ord(data[option_pointer])+ord(data[option_pointer+1])
        #print "xaviP="+str(xaviPayload)
        #cmd = 'wget "http://openwsnstats.appspot.com/rest/stats?sid=1&nid=1&rssi='+str(xaviPayload)+'&numtx=10&numrx=20&numack=10&cost=1.0"'
        #print cmd
        #os.system(cmd)
        #print "poipoi stop"
	
        payload=""
        #try:
        #    for i in range(len(data[option_pointer:])-1):
        #        payload += hex(struct.unpack('b',data[option_pointer+i:option_pointer+i+1])[0]) #data[option_pointer:]
        #except:
	#    for i in range(len(data[option_pointer:])-1):
        #        payload += hex(struct.unpack('b',data[option_pointer+i:option_pointer+i+1])[0])

        payload = binascii.hexlify(data[option_pointer:])

        print "addr", address
        print "version ", version
        print "type ", type
        print "options ", options
        print "code ", code 
        print "mId", mId
        print "optionList (delta, length, str)", optionList
        print "payload ",  payload
	
	#write the data to file if we're intereted in it
	if (code == 3 or code == 2) and address[0][0:2] != "00":
		print "writing file"
		if not os.path.exists("/var/www/data/" + address[0]):
    			os.makedirs("/var/www/data/" + address[0])
		sensor_name = ""
		now = datetime.datetime.now()
		for option in optionList:
			if option[2] == 'Location-Path':
				filepath = "/var/www/data/"+address[0]+"/" + option[3]+".txt"
				f = open(filepath,"a")
				if os.path.getsize(filepath)==0:
					f.write('logtime,coap-payload-hex'+ "\n")
				writeline = ""
				writeline += str(now) + ","
                                print "payload xv ",  payload
				writeline += payload
				f.write(writeline + "\n")
				f.close()
		#dump everythign else in a "raw" file for debugging
		f_raw = open("/var/www/data/"+address[0]+"/raw.txt","a")
		f_raw.write(str(now) + "," + binascii.hexlify(data) + "\n")
		f_raw.close()
	
   #except:
   #	print "Error parsing packet. This demo server only supports a barebone coap post/put implementation."

socket_handler = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
socket_handler.bind(('',port))
while True:
   raw,conn = socket_handler.recvfrom(1024)
   print raw
   parseCoapData(raw, conn)
   #print 'version='+str( (ord(raw[0])& 0xc0) >> 6)
   print binascii.hexlify(raw)
