import sys

from openTranslator import openTranslator
from openUI         import openDisplay
import shared
import struct

recordElements     = {}
printParsingErrors = False
OpenTranslator     = openTranslator() #create opentranslator object

command_length = {}
command_length['recordID']           =  3
command_length['recordIsSync']       =  5
command_length['recordIDManager']    = 74
command_length['recordMyDAGrank']    =  5
command_length['recordOutputBuffer'] =  8
command_length['recordAsn']          =  6
command_length['recordMacStats']     =  4+7
command_length['recordScheduleRow']  = 36
command_length['recordNeighborsRow'] = 36
command_length['recordQueueRow']     = 14
command_length['recordError']        =  9
command_length['recordData']         =  5

#============================ initialization ==================================

def createRecordElement(motePort):
   recordElements[motePort] = {}
   recordElements[motePort]["addr_16b"]                 = "?"
   recordElements[motePort]["asn"]                      = 0
   recordElements[motePort]["schedule"]                 = {}
   recordElements[motePort]["schedule"]["contentRows"]  = {}
   recordElements[motePort]["queue"]                    = {}
   recordElements[motePort]["queue"]["contentRows"]     = {}
   recordElements[motePort]["neighbors"]                = {}
   recordElements[motePort]["neighbors"]["contentRows"] = {}

#============================ parseInput ======================================

def parseInput(motePort,input):
   while True:
      if (len(input)<1):
         return
      #byte 0 is the type of status message
      if   (input[0]=="S"):    #status
         if (len(input)<4):
            if (printParsingErrors):
               openDisplay.printError("input too short to be a status ("+str(len(input))+" chars)")
            return
         #bytes 1 and 2 is ID
         recordID(motePort, input)
         #byte 3 is statusElementNumber
         statusElementNumber=ord(input[3])
         if   (statusElementNumber==0):
            current_command_length = command_length['recordIsSync']
            recordIsSync(motePort,input[0:current_command_length])
         elif (statusElementNumber==1):
            current_command_length = command_length['recordIDManager']
            recordIDManager(motePort,input[0:current_command_length])
         elif (statusElementNumber==2):
            current_command_length = command_length['recordMyDAGrank']
            recordMyDAGrank    (motePort,input[0:current_command_length])
         elif (statusElementNumber==3):
            current_command_length = command_length['recordOutputBuffer']
            recordOutputBuffer (motePort,input[0:current_command_length])
         elif (statusElementNumber==4):
            current_command_length = command_length['recordAsn']
            recordAsn(motePort,input[0:current_command_length])
         elif (statusElementNumber==5):
            current_command_length = command_length['recordMacStats']
            recordMacStats(motePort,input[0:current_command_length])
         elif (statusElementNumber==6):
            current_command_length = command_length['recordScheduleRow']
            recordScheduleRow(motePort,input[0:current_command_length])
         elif (statusElementNumber==7):
            current_command_length = command_length['recordQueueRow']
            recordQueueRow     (motePort,input[0:current_command_length])
         elif (statusElementNumber==8):
            current_command_length = command_length['recordNeighborsRow']
            recordNeighborsRow(motePort,input[0:current_command_length])
         else:
            if (printParsingErrors):
               openDisplay.printError("Unknown statusElementNumber="+str(statusElementNumber))
            return
      elif (input[0]=="E"):  #error
         current_command_length = command_length['recordError']
         recordError(motePort,input[0:current_command_length])
      elif (input[0]=="D"):  #data
         current_command_length = command_length['recordData']
         #recordData(motePort,input[0:current_command_length])
         recordData(motePort,input)
      else:
         if (printParsingErrors):
            openDisplay.printError("status message of unknown type="+input[0])
         return
      input = input[current_command_length:]

#============================ record functions ================================

def recordID(motePort,input):
   if (len(input)<command_length['recordID']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordID'])+\
               " in recordID from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #bytes 1 and 2 is addr_16b
   recordElements[motePort]["addr_16b"]  = ord(input[1])*(256**0)
   recordElements[motePort]["addr_16b"] += ord(input[2])*(256**1)
   recordElements[motePort]["addr_16b"]  = hex(recordElements[motePort]["addr_16b"])
   openDisplay.displayID(motePort)

def recordIsSync(motePort,input):
   if (len(input)!=command_length['recordIsSync']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordIsSync'])+\
               " in recordIsSync from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #byte 4 is isSync
   recordElements[motePort]["isSync"] = ord(input[4])
   openDisplay.displayIsSync(motePort)
   
def recordIDManager(motePort,input):
   if (len(input)!=command_length['recordIDManager']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordIDManager'])+\
               " in recordIDManager from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #byte 4 is isDAGroot
   recordElements[motePort]["isDAGroot"] = ord(input[4])
   #byte 5 is isBridge
   recordElements[motePort]["isBridge"]  = ord(input[5])
   if recordElements[motePort]["isBridge"]==1:
      shared.portBridgeMote = motePort
   #byte 6 is unused
   #byte 7,8 is my16bID
   recordElements[motePort]["my16bID"]   = ord(input[7])*(256**1)
   recordElements[motePort]["my16bID"]  += ord(input[8])*(256**0)
   recordElements[motePort]["my16bID"]   = hex(recordElements[motePort]["my16bID"])
   #byte 24-31 is my64bID
   recordElements[motePort]["my64bID"]   = ord(input[24])*(256**7)
   recordElements[motePort]["my64bID"]  += ord(input[25])*(256**6)
   recordElements[motePort]["my64bID"]  += ord(input[26])*(256**5)
   recordElements[motePort]["my64bID"]  += ord(input[27])*(256**4)
   recordElements[motePort]["my64bID"]  += ord(input[28])*(256**3)
   recordElements[motePort]["my64bID"]  += ord(input[29])*(256**2)
   recordElements[motePort]["my64bID"]  += ord(input[30])*(256**1)
   recordElements[motePort]["my64bID"]  += ord(input[31])*(256**0)
   recordElements[motePort]["my64bID"]   = hex(recordElements[motePort]["my64bID"])
   #byte 41,42 is myPANID
   recordElements[motePort]["myPANID"]   = ord(input[41])*(256**1)
   recordElements[motePort]["myPANID"]  += ord(input[42])*(256**0)
   recordElements[motePort]["myPANID"]   = hex(recordElements[motePort]["myPANID"])
   #byte 58-65 is myPrefix
   recordElements[motePort]["myPrefix"]  = ord(input[58])*(256**7)
   recordElements[motePort]["myPrefix"] += ord(input[59])*(256**6)
   recordElements[motePort]["myPrefix"] += ord(input[60])*(256**5)
   recordElements[motePort]["myPrefix"] += ord(input[61])*(256**4)
   recordElements[motePort]["myPrefix"] += ord(input[62])*(256**3)
   recordElements[motePort]["myPrefix"] += ord(input[63])*(256**2)
   recordElements[motePort]["myPrefix"] += ord(input[64])*(256**1)
   recordElements[motePort]["myPrefix"] += ord(input[65])*(256**0)
   recordElements[motePort]["myPrefix"]  = hex(recordElements[motePort]["myPrefix"])
   openDisplay.displayIDManager(motePort)
   
def recordMyDAGrank(motePort,input):
   if (len(input)!=command_length['recordMyDAGrank']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordMyDAGrank'])+\
               " in recordMyDAGrank from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #byte 4 is myDAGrank
   recordElements[motePort]["myDAGrank"] = ord(input[4])
   openDisplay.displayMyDAGrank(motePort)

def recordOutputBuffer(motePort,input):
   if (len(input)!=command_length['recordOutputBuffer']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordOutputBuffer'])+\
               " in recordOutputBuffer from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #bytes 4 and 5 is output_buffer_index_write (little endian)
   recordElements[motePort]["output_buffer_index_write"]  = ord(input[4])*(256**0)
   recordElements[motePort]["output_buffer_index_write"] += ord(input[5])*(256**1)
   #bytes 6 and 7 is output_buffer_index_read (little endian)
   recordElements[motePort]["output_buffer_index_read"]   = ord(input[6])*(256**0)
   recordElements[motePort]["output_buffer_index_read"]  += ord(input[7])*(256**1)
   openDisplay.displayOutputBuffer(motePort)

def recordAsn(motePort,input):
   if (len(input)!=command_length['recordAsn']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordAsn'])+\
               " in recordAsn from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #bytes 4 & 5 is asn
   recordElements[motePort]["asn"]=ord(input[4])+256*ord(input[5])
   openDisplay.displayAsn(motePort)

def recordMacStats(motePort,input):
   if (len(input)!=command_length['recordMacStats']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordMacStats'])+\
               " in recordMacStats from node="+str(recordElements[motePort]["addr_16b"]))
      return
   '''
   for i in range(0,len(input)):
      print str(i)+':'+str(ord(input[i]))
   '''
   # B: syncCounter
   # x: pad byte
   # h: minCorrection
   # h: maxCorrection
   # B: numDeSync
   (
    recordElements[motePort]["syncCounter"],
    recordElements[motePort]["minCorrection"],
    recordElements[motePort]["maxCorrection"],
    recordElements[motePort]["numDeSync"]
   ) = struct.unpack('BxhhB',input[4:11])
   openDisplay.displayMacStats(motePort)
   
def recordScheduleRow(motePort,input):
   '''
   counter = 0
   for char in input:
      print str(counter)+" : "+hex(ord(char))
      counter += 1
   '''
   if (len(input)!=command_length['recordScheduleRow']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordScheduleRow'])+\
               " in recordScheduleRow from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #byte 4 is rowNumber
   rowNumber = ord(input[4])
   
   recordElements[motePort]["schedule"]["contentRows"][rowNumber] = {}
   (
                                                                                              #[5]     x
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["type"],                    #[6]     B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["shared"],                  #[7]     B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["backoffExponent"],         #[8]     B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["backoff"],                 #[9]     B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["channelOffset"],           #[10]    B
   addrType,                                                                                  #[11]    B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["neighbor"],                #[12-19] Q
                                                                                              #[20-27] xxxxxxx
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["numRx"],                   #[28]    B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["numTx"],                   #[29]    B
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["numTxACK"],                #[30]    B
   ) = struct.unpack('>xBBBBBBQxxxxxxxxBBB',input[5:31])
   
   if (addrType==6):
      recordElements[motePort]["schedule"]["contentRows"][rowNumber]["neighbor"] = "ANY"
   else:
      recordElements[motePort]["schedule"]["contentRows"][rowNumber]["neighbor"] = hex(recordElements[motePort]["schedule"]["contentRows"][rowNumber]["neighbor"])
   
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["type"] = \
      OpenTranslator.translateCellType(recordElements[motePort]["schedule"]["contentRows"][rowNumber]["type"])
   
   (
   recordElements[motePort]["schedule"]["contentRows"][rowNumber]["asn"],                     #I
   ) = struct.unpack('<I',input[command_length['recordScheduleRow']-4:command_length['recordScheduleRow']])
   
   #cost
   if (recordElements[motePort]["schedule"]["contentRows"][rowNumber]["numTxACK"]==0):
      recordElements[motePort]["schedule"]["contentRows"][rowNumber]["cost"]="-"
   else:
      recordElements[motePort]["schedule"]["contentRows"][rowNumber]["cost"]="%.1f"%(
         (
            float(recordElements[motePort]["schedule"]["contentRows"][rowNumber]["numTx"])
            /
            float(recordElements[motePort]["schedule"]["contentRows"][rowNumber]["numTxACK"])
         )*10.0
      )
   openDisplay.displaySchedule(motePort,rowNumber)

def recordQueueRow(motePort,input):
   if (len(input)!=command_length['recordQueueRow']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordQueueRow'])+\
               " in recordQueueRow from node="+str(recordElements[motePort]["addr_16b"]))
      return
   for rowNumber in range(0,5):
      recordElements[motePort]["queue"]["contentRows"][rowNumber] = {}
      #first byte is creator
      creator = OpenTranslator.translateComponentCode(ord(input[4+2*rowNumber]))
      recordElements[motePort]["queue"]["contentRows"][rowNumber]["creator"] = creator
      #second byte is owner
      owner = OpenTranslator.translateComponentCode(ord(input[5+2*rowNumber]))
      recordElements[motePort]["queue"]["contentRows"][rowNumber]["owner"] = owner
   openDisplay.displayQueue(motePort)

def recordNeighborsRow(motePort,input):
   ''''
   counter = 0
   for char in input:
      print str(counter)+" : "+hex(ord(char))
      counter += 1
   '''
   if (len(input)!=command_length['recordNeighborsRow']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordNeighborsRow'])+\
               " in recordNeighborsRow from node="+str(recordElements[motePort]["addr_16b"]))
      return
   # bytes 4,5: rowNumber (little endian)
   rowNumber  = ord(input[4])*(256**0)
   rowNumber += ord(input[5])*(256**1)
   
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber] = {}
  
   (
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["used"],                    #B
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["parentPreference"],        #B
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["stableNeighbor"],          #B
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["switchStabilityCounter"],  #B
                                                                                               #x
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["addr_64b"],                #Q
                                                                                               #xxxxxxx
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["DAGrank"],                 #B
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["rssi"],                    #b
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["numRx"],                   #B
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["numTx"],                   #B
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["numTxACK"],                #B
   ) = struct.unpack('>BBBBxQxxxxxxxxBbBBB',input[6:command_length['recordNeighborsRow']-4])
   
   (
   recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["asn"],                     #I
   ) = struct.unpack('<I',input[command_length['recordNeighborsRow']-4:command_length['recordNeighborsRow']])
   
   #cost
   if (recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["numTxACK"]==0):
      recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["cost"]="-"
   else:
      recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["cost"]="%.1f"%(
         (
            float(recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["numTx"])
            /
            float(recordElements[motePort]["neighbors"]["contentRows"][rowNumber]["numTxACK"])
         )*10.0
      )
   openDisplay.displayNeighbors(motePort,rowNumber)

def recordError(motePort,input):
   if (len(input)!=command_length['recordError']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordError'])+\
               " in recordError from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #byte 3 is componentCode
   componentCode = ord(input[3])
   #byte 4 is errorCode
   errorCode = ord(input[4])
   #bytes 5 and 6 is arg1
   arg1 = ord(input[5])*256+ord(input[6])
   #bytes 7 and 8 is arg2
   arg2 = ord(input[7])*256+ord(input[8])
   errorString,seriousness = OpenTranslator.translateErrortoString(recordElements[motePort]["addr_16b"],componentCode,errorCode,arg1,arg2)
   openDisplay.displayError(motePort,errorString,seriousness)

def recordData(motePort,input):
   if (len(input)<command_length['recordData']):
      if (printParsingErrors):
         openDisplay.printError("wrong input size="+\
               str(len(input))+"!="+str(command_length['recordData'])+\
               " in recordData from node="+str(recordElements[motePort]["addr_16b"]))
      return
   #bytes 3+ is data
   recordElements[motePort]["sensorData"]=input[3:]
   shared.lbrClientThread.send(input[3:])
   #openDisplay.displayData(motePort) do not display data
