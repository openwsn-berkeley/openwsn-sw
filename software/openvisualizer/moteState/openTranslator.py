class openTranslator:   
   def __init__(self):
      self.componentIdentifiers = {}
      self.errorCodes = {}
      #read Indentifier/Error codes from file
      import os
      import re
      # since we need to read a file that's multiple parent directories away
      # we need to descend to the lower dir's and find "openwsn.h"
      # assume openwsn.h is in .../firmware/openos/openwsn/openwsn.h"
      #filename = os.getcwd().split(os.sep).pop().pop().append("firmware").append("openos").append("openwsn").append("openwsn.h")
      filename = os.getcwd().split(os.sep)
      filename.pop()
      filename.pop()
      filename.pop()
      filename.pop()
      filename.append("firmware")
      filename.append("openos")
      filename.append("openwsn")
      filename.append("openwsn.h")
      parsingState = 'nothing' # 0=nothing, 1=component parsing, 2=errorParsing
      try:
         for line in open(str.join(os.sep, filename)):
            if(line.strip()=="//component identifiers"):
               parsingState = 'componentIdentifiers' 
            elif (line.strip()=="//error codes"):
               parsingState = 'errorCodes'
            elif (line.strip()=="};"): #redundant, but works
               parsingState = 'nothing'

            if (parsingState=='componentIdentifiers'):
               #do a regular expression search, if it rerutns group(1) will be our error ID, and group(2) holds the error #
               #the error ID has to be converted from hex to int also
               match = re.search('(.*)=(.*),',line)
               if(match):
                  #print match.group(1)
                  #print match.group(1).strip() + " " + match.group(2) + " " + str(int(match.group(2),16))
                  self.componentIdentifiers[int(match.group(2),16)] = match.group(1).strip()
            elif (parsingState=='errorCodes'):
               match = re.search('(.*)=(.*),.*//(.*?)\[(.*)\](.*)',line)
               if(match):
                  #match.group(1) = ID
                  #match.group(2) = #
                  #match.group(3) = comment
                  #match.group(4) = componentID
                  #match.group(5) = arg comments //can be split into arg1 and arg2
                  errArray = []
                  errArray.append(match.group(1).strip())
                  errArray.append(match.group(3).strip())
                  errArray.append(match.group(4).strip())
                  #parse arguments
                  args = []
                  args.append("")
                  args.append("")
                  if(match.group(5).find("arg2")>0):
                     matchArgs = re.search('arg1=(.*)arg2=(.*)',match.group(5).strip())
                     if(matchArgs):
                        args[0] = (matchArgs.group(1).strip())
                        args[1] = (matchArgs.group(2).strip())
                  elif(match.group(5).find("arg1")>0):
                     matchArgs = re.search('arg1=(.*)',match.group(5).strip())
                     if(matchArgs):
                        args[0] = (matchArgs.group(1).strip())
                        args[1] = ""
                  
                  #append arguments to error array
                  errArray.append(args[0])
                  errArray.append(args[1])
                  
                  self.errorCodes[int(match.group(2).strip(),16)] = errArray
      except:
           print "Error reading openwsn.h. Tried reading {0}".format('/'.join(filename))
      
   def translateIEEE802154EState(sefl,state):
      if   (state== 0): return "S_SYNCHRONIZING"
      elif (state== 1): return "S_TX_TXDATAPREPARE"
      elif (state== 2): return "S_TX_TXDATAREADY"
      elif (state== 3): return "S_TX_TXDATA"
      elif (state== 4): return "S_TX_RXACKPREPARE"
      elif (state== 5): return "S_TX_RXACKREADY"
      elif (state== 6): return "S_TX_RXACK"
      elif (state== 7): return "S_RX_RXDATAPREPARE"
      elif (state== 8): return "S_RX_RXDATAREADY"
      elif (state== 9): return "S_RX_RXDATA"
      elif (state==10): return "S_RX_TXACKPREPARE"
      elif (state==11): return "S_RX_TXACKREADY"
      elif (state==12): return "S_RX_TXACK"
      elif (state==13): return "S_SLEEP"
      else: return "unknown state="+str(state)

   def translateRadioState(self,state):
      if   (state==0): return "S_STOPPED"
      elif (state==1): return "S_STARTING_VREG"
      elif (state==2): return "S_STARTING_OSCILLATOR"
      elif (state==3): return "S_STARTED"
      elif (state==4): return "S_LOADING_PACKET"
      elif (state==5): return "S_SETTING_CHANNEL"
      elif (state==6): return "S_READY_TX"
      elif (state==7): return "S_TRANSMITTING"
      elif (state==8): return "S_READY_RX"
      elif (state==9): return "S_RECEIVING"
      elif (state==10):return "S_STOPPING"
      else: return "unknown state="+str(state)

   def translateTransmitState(self,state):
      if   (state==0): return "STOPPED"
      elif (state==1): return "STARTED"
      elif (state==2): return "LOAD"
      elif (state==3): return "LOADED"
      elif (state==4): return "SFD"
      elif (state==5): return "EFD"
      else: return "unknown state="+str(state)

   def translateTCPState(self,state):
      if   (state==0):  return "CLOSED"
      elif (state==1):  return "ALMOST_SYN_RECEIVED"
      elif (state==2):  return "SYN_RECEIVED"
      elif (state==3):  return "ALMOST_SYN_SENT"
      elif (state==4):  return "SYN_SENT"
      elif (state==5):  return "ALMOST_ESTABLISHED"
      elif (state==6):  return "ESTABLISHED"
      elif (state==7):  return "ALMOST_DATA_SENT"
      elif (state==8):  return "DATA_SENT"
      elif (state==9):  return "ALMOST_DATA_RECEIVED"
      elif (state==10): return "ALMOST_FIN_WAIT_1"
      elif (state==11): return "FIN_WAIT_1"
      elif (state==12): return "ALMOST_CLOSING"
      elif (state==13): return "CLOSING"
      elif (state==14): return "FIN_WAIT_2"
      elif (state==15): return "ALMOST_TIME_WAIT"
      elif (state==16): return "TIME_WAIT"
      elif (state==17): return "ALMOST_CLOSE_WAIT"
      elif (state==18): return "CLOSE_WAIT"
      elif (state==19): return "ALMOST_LAST_ACK"
      elif (state==20): return "LAST_ACK"
      else: return "unknown state="+str(state)

   def translateComponentCode(self,componentCode):
      try:
         return self.componentIdentifiers[componentCode].strip('COMPONENT_')
      except:
         return "unknown component="+str(componentCode)

   def translateAddressType(self,addressType):
      if   (addressType==0): return "NONE"
      elif (addressType==1): return "16B"
      elif (addressType==2): return "64B"
      elif (addressType==3): return "128B"
      elif (addressType==4): return "PANID"
      elif (addressType==5): return "PREFIX"
      elif (addressType==6): return "ANYCAST"
      else: return "unknown addressType="+str(addressType)

   def translateCellType(self,cellType):
      if   (cellType==0):return "OFF"
      elif (cellType==1):return "ADV"
      elif (cellType==2):return "TX"
      elif (cellType==3):return "RX"
      elif (cellType==4):return "TXRX"
      elif (cellType==5):return "SERIALRX"
      elif (cellType==6):return "MORESERIALRX"
      else: return "unknown cellType="+str(cellType)

   def translateRawRSSItodBm(self,rawRSSI):
      if (rawRSSI>128):
         dBmRSSI=0
         for i in range(8):
            if ((rawRSSI & (1<<i))>>i)==0:
               dBmRSSI=dBmRSSI|(1<<i)
         dBmRSSI=-(dBmRSSI+1)
      else:
         dBmRSSI=rawRSSI
      dBmRSSI=dBmRSSI-45
      return dBmRSSI

   def translateErrortoString(self,ID,componentCode,errorCode,arg1,arg2):
      errorString=str(ID)+": "
      if errorCode in self.errorCodes:
         errorString+="["+self.translateComponentCode(componentCode)+"] "
         errorArray = self.errorCodes[errorCode]
         errorString+=errorArray[1]
         if(errorArray[3] != ""):
            errorString+= " " + errorArray[3] + "=" + str(arg1)
         
         if(errorArray[4] != ""):
            errorString+= " " + errorArray[4] + "=" + str(arg2)
         seriousness="error"
      else:
         return "unknown error="+str(errorCode)
      errorString+="\n"
      return errorString, seriousness     

   def translateAddress(self,input):
      if len(input)!=17:
         print '[openTranslator] ERROR translateAddress wrong address length'
      output = ''
      addressType = ord(input[0])
      if (addressType>=1 and addressType<=5):
         output += '%.2X'%ord(input[1])
         output += '%.2X'%ord(input[2])
         if (addressType==2 or addressType==3 or addressType==5):
            output += '%.2X'%ord(input[3])
            output += '%.2X'%ord(input[4])
            output += '%.2X'%ord(input[5])
            output += '%.2X'%ord(input[6])
            output += '%.2X'%ord(input[7])
            output += '%.2X'%ord(input[8])
            if (addressType==3):
               output += '%.2X'%ord(input[ 9])
               output += '%.2X'%ord(input[10])
               output += '%.2X'%ord(input[11])
               output += '%.2X'%ord(input[12])
               output += '%.2X'%ord(input[13])
               output += '%.2X'%ord(input[14])
               output += '%.2X'%ord(input[15])
               output += '%.2X'%ord(input[16])
      return output