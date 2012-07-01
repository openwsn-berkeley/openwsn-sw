import os, threading, datetime, sys
import Tkinter
import socket
import binascii
from processing import shared
from processing import openRecord

#========================= variables ==============================================================

debugOpenDisplay         =     False

location                 =        ''
RX_IMAGE_HEIGHT          =       300
RX_IMAGE_WIDTH           =       400
TEXTHEIGHT               =        10
TEXTWIDTH                =        37
GRAPHSIZE_DEFAULT        =       300
GRAPHSIZE_471            =       420
GRAPHSIZE_JOPPA_WIDTH    =       300
GRAPHSIZE_JOPPA_HEIGHT   =       534
GRAPHMOTESIZE            =        20
SWITCHSTABILITYTHRESHOLD =         5

moteLocationDefault={}
moteLocationDefault["0xb6"]=(150, 50)
moteLocationDefault["0x99"]=( 50,250)
moteLocationDefault["0x8b"]=(250,250)

moteLocationCory471={}
moteLocationCory471["0xb6"]=(106,241)
moteLocationCory471["0x99"]=(111,216)
moteLocationCory471["0x8b"]=(86,246)

moteLocationJoppa={}
moteLocationJoppa["0x1"]=(97,76)

color={}
color["unstableneighbor"] = '#AAAAAA'
color["stableneighbor"]   = '#555555'
color["scheduledSlotS"]   = '#FF8000'
color["scheduledSlotP"]   = '#FF0000'
color["mote"]             = '#A0CBE2'
color["updatedLatest"]    = 'yellow'
color["updatedOld"]       = 'grey'
color["isSynced"]         = '#99FF66'
color["isNotSynced"]      = '#CC9966'

tkSemaphore = threading.BoundedSemaphore()
column_counter = 0

displayElements = {}

#============================ initialization ==================================

def createDisplayElement(motePort):
   global column_counter
   column_counter += 1
   tkSemaphore.acquire()
   displayElements[motePort] = {}
   displayElements[motePort]["CheckbuttonVar"]=Tkinter.IntVar()
   displayElements[motePort]["Checkbutton"]=Tkinter.Checkbutton(showDetailButtonFrame,text="?",command=showDetails,\
         variable=displayElements[motePort]["CheckbuttonVar"])
   displayElements[motePort]["Checkbutton"].grid(row=1,column=column_counter)
   #---mote frame
   displayElements[motePort]["moteFrame"]=Tkinter.Frame(rightFrame,borderwidth=1,relief=Tkinter.SUNKEN)
   #header
   displayElements[motePort]["IDManager"]    = Tkinter.Label(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["IDManager"].config(justify=Tkinter.LEFT)
   displayElements[motePort]["IDManager"].config(text='IDManager=?')
   displayElements[motePort]["IDManager"].grid(row=1,column=1)
   displayElements[motePort]["myDAGrank"]    = Tkinter.Label(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["myDAGrank"].config(justify=Tkinter.LEFT)
   displayElements[motePort]["myDAGrank"].config(text='myDAGrank=?')
   displayElements[motePort]["myDAGrank"].grid(row=1,column=2)
   displayElements[motePort]["outputBuffer"] = Tkinter.Label(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["outputBuffer"].config(justify=Tkinter.LEFT)
   displayElements[motePort]["outputBuffer"].config(text='outputBuffer=?')
   displayElements[motePort]["outputBuffer"].grid(row=1,column=3)
   displayElements[motePort]["asn"]         = Tkinter.Label(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["asn"].grid(row=1,column=4)
   displayElements[motePort]["asn"].config(justify=Tkinter.LEFT)
   displayElements[motePort]["asn"].config(text='asn=?')
   displayElements[motePort]["macStats"]         = Tkinter.Label(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["macStats"].grid(row=1,column=5)
   displayElements[motePort]["macStats"].config(justify=Tkinter.LEFT)
   displayElements[motePort]["macStats"].config(text='macStats=?')
   displayElements[motePort]["motePort"]     = Tkinter.Label(displayElements[motePort]["moteFrame"])
   temp_address, temp_port = motePort
   displayElements[motePort]["motePort"].config(text=temp_address+":"+str(temp_port))
   displayElements[motePort]["motePort"].grid(row=1,column=6)
   #destination address fields
   displayElements[motePort]["destination_fields"] = {}
   displayElements[motePort]["destination_fields"]["frame"] = Tkinter.Frame(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["destination_fields"]["frame"].grid(row=2,column=1,columnspan=6)
   #--destination address
   displayElements[motePort]["destination_fields"]["address_string"]=Tkinter.StringVar()
   #displayElements[motePort]["destination_fields"]["address_string"].set("200104701f040fe30000000000000002")
   #displayElements[motePort]["destination_fields"]["address_string"].set("200104701f05098e0000000000000002")
   displayElements[motePort]["destination_fields"]["address_string"].set("200104701f040dff0000000000000002")
   displayElements[motePort]["destination_fields"]["address_field"]=Tkinter.Entry(
         displayElements[motePort]["destination_fields"]["frame"],width=32,
         textvariable=displayElements[motePort]["destination_fields"]["address_string"])
   displayElements[motePort]["destination_fields"]["address_field"].grid(row=1,column=1)
   #--destination port
   displayElements[motePort]["destination_fields"]["port_string"]=Tkinter.StringVar()
   displayElements[motePort]["destination_fields"]["port_string"].set('8080')
   displayElements[motePort]["destination_fields"]["port_field"]=Tkinter.Entry(
         displayElements[motePort]["destination_fields"]["frame"],width=10,
         textvariable=displayElements[motePort]["destination_fields"]["port_string"])
   displayElements[motePort]["destination_fields"]["port_field"].grid(row=1,column=2)
   #command buttons
   displayElements[motePort]["commands"] = {}
   displayElements[motePort]["commands"]["frame"] = Tkinter.Frame(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["commands"]["frame"].grid(row=3,column=1,columnspan=6)
   #--TCPInject
   temp_lambda = lambda x=motePort:sendCommandTCPInject(x)
   displayElements[motePort]["commands"]["TCPInjectButton"] = Tkinter.Button(
         displayElements[motePort]["commands"]["frame"],text="TCPInject",command=temp_lambda)
   displayElements[motePort]["commands"]["TCPInjectButton"].grid(row=1,column=1)
   #--UDPInject
   temp_lambda = lambda x=motePort:sendCommandUDPInject(x)
   displayElements[motePort]["commands"]["UDPInjectButton"] = Tkinter.Button(
         displayElements[motePort]["commands"]["frame"],text="UDPInject",command=temp_lambda)
   displayElements[motePort]["commands"]["UDPInjectButton"].grid(row=1,column=2)
   #--UDPSensor
   temp_lambda = lambda x=motePort:sendCommandUDPSensor(x)
   displayElements[motePort]["commands"]["UDPSensorButton"] = Tkinter.Button(
         displayElements[motePort]["commands"]["frame"],text="UDPSensor",command=temp_lambda)
   displayElements[motePort]["commands"]["UDPSensorButton"].grid(row=1,column=3)
   #--ICMPv6Echo
   temp_lambda = lambda x=motePort:sendCommandICMPv6Echo(x)
   displayElements[motePort]["commands"]["ICMPv6EchoButton"] = Tkinter.Button(
         displayElements[motePort]["commands"]["frame"],text="ICMPv6Echo",command=temp_lambda)
   displayElements[motePort]["commands"]["ICMPv6EchoButton"].grid(row=1,column=4)
   #--ICMPv6Router
   temp_lambda = lambda x=motePort:sendCommandICMPv6Router(x)
   displayElements[motePort]["commands"]["ICMPv6RouterButton"] = Tkinter.Button(
         displayElements[motePort]["commands"]["frame"],text="ICMPv6Router",command=temp_lambda)
   displayElements[motePort]["commands"]["ICMPv6RouterButton"].grid(row=1,column=5)
   #--ICMPv6RPL
   temp_lambda = lambda x=motePort:sendCommandICMPv6RPL(x)
   displayElements[motePort]["commands"]["ICMPv6RPLButton"] = Tkinter.Button(
         displayElements[motePort]["commands"]["frame"],text="ICMPv6RPL",command=temp_lambda)
   displayElements[motePort]["commands"]["ICMPv6RPLButton"].grid(row=1,column=6)
   #schedule
   displayElements[motePort]["schedule"] = {}
   displayElements[motePort]["schedule"]["frame"]=Tkinter.Frame(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["schedule"]["frame"].grid(row=4,column=1,columnspan=3)
   displayElements[motePort]["schedule"]["Label"]=Tkinter.Label(displayElements[motePort]["schedule"]["frame"])
   displayElements[motePort]["schedule"]["Label"].config(text='schedule')
   displayElements[motePort]["schedule"]["Label"].grid(row=1)
   displayElements[motePort]["schedule"]["Table"]=Tkinter.Label(displayElements[motePort]["schedule"]["frame"])
   displayElements[motePort]["schedule"]["Table"].config(background='white',borderwidth=2,relief=Tkinter.RIDGE)
   displayElements[motePort]["schedule"]["Table"].grid(row=2)
   #queue
   displayElements[motePort]["queue"] = {}
   displayElements[motePort]["queue"]["frame"]=Tkinter.Frame(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["queue"]["frame"].grid(row=4,column=5,columnspan=3)
   displayElements[motePort]["queue"]["Label"]=Tkinter.Label(displayElements[motePort]["queue"]["frame"])
   displayElements[motePort]["queue"]["Label"].config(text='queue')
   displayElements[motePort]["queue"]["Label"].grid(row=1)
   displayElements[motePort]["queue"]["Table"]=Tkinter.Label(displayElements[motePort]["queue"]["frame"])
   displayElements[motePort]["queue"]["Table"].config(background='white',width=30)
   displayElements[motePort]["queue"]["Table"].config(borderwidth=2,relief=Tkinter.RIDGE)
   displayElements[motePort]["queue"]["Table"].grid(row=2)
   #neighbors
   displayElements[motePort]["neighbors"] = {}
   displayElements[motePort]["neighbors"]["frame"]=Tkinter.Frame(displayElements[motePort]["moteFrame"])
   displayElements[motePort]["neighbors"]["frame"].grid(row=5,column=1,columnspan=7)
   displayElements[motePort]["neighbors"]["Label"]=Tkinter.Label(displayElements[motePort]["neighbors"]["frame"])
   displayElements[motePort]["neighbors"]["Label"].config(text='neighbors')
   displayElements[motePort]["neighbors"]["Label"].grid(row=1)
   displayElements[motePort]["neighbors"]["Table"]=Tkinter.Label(displayElements[motePort]["neighbors"]["frame"])
   displayElements[motePort]["neighbors"]["Table"].config(background='white')
   displayElements[motePort]["neighbors"]["Table"].config(borderwidth=2,relief=Tkinter.RIDGE)
   displayElements[motePort]["neighbors"]["Table"].grid(row=2)
   tkSemaphore.release()

#============================ send functions ==================================
   
def sendCommandTCPInject(motePort):
   print "TCPInject at",
   if checkValidDestinationAddress(motePort):
      output  = retrieveDestinationAddress(motePort)
      output += retrieveDestinationPort(motePort)
      output  = 'T' + chr(len(output)) + output
      #print "ouput: "+output+" ("+str(len(output))+")"
      shared.moteConnectors[motePort].write(output)

def sendCommandUDPInject(motePort):
   print "UDPInject at",
   if checkValidDestinationAddress(motePort):
      output  = retrieveDestinationAddress(motePort)
      output += retrieveDestinationPort(motePort)
      output  = 'U' + chr(len(output)) + output
      #print "ouput: "+output+" ("+str(len(output))+")"
      shared.moteConnectors[motePort].write(output)

def sendCommandUDPSensor(motePort):
   print "UDPSensor at",
   if checkValidDestinationAddress(motePort):
      output  = retrieveDestinationAddress(motePort)
      output += retrieveDestinationPort(motePort)
      output  = 'S' + chr(len(output)) + output
      #print "ouput: "+output+" ("+str(len(output))+")"
      shared.moteConnectors[motePort].write(output)

def sendCommandICMPv6Echo(motePort):
   print "ICMPv6Echo at",
   if checkValidDestinationAddress(motePort):
      output  = retrieveDestinationAddress(motePort)
      output  = 'E' + chr(len(output)) + output
      #print "ouput: "+output+" ("+str(len(output))+")"
      shared.moteConnectors[motePort].write(output)

def sendCommandICMPv6Router(motePort):
   print "ICMPv6Router at",
   if checkValidDestinationAddress(motePort):
      output  = retrieveDestinationAddress(motePort)
      output  = 'O' + chr(len(output)) + output
      #print "ouput: "+output+" ("+str(len(output))+")"
      shared.moteConnectors[motePort].write(output)

def sendCommandICMPv6RPL(motePort):
   print "ICMPv6RPL at",
   if checkValidDestinationAddress(motePort):
      output  = retrieveDestinationAddress(motePort)
      output  = 'P' + chr(len(output)) + output
      #print "ouput: "+output+" ("+str(len(output))+")"
      shared.moteConnectors[motePort].write(output)

def checkValidDestinationAddress(motePort):
   tkSemaphore.acquire()
   address = displayElements[motePort]["destination_fields"]["address_string"].get()
   port    = displayElements[motePort]["destination_fields"]["port_string"].get()
   tkSemaphore.release()
   print str(motePort),
   print "for "+address+"%"+port
   return_value = True
   if len(address)==32:
      try:
         binascii.unhexlify(address)
         tkSemaphore.acquire()
         displayElements[motePort]["destination_fields"]["address_field"].config(background="green")
         tkSemaphore.release()
      except:
         tkSemaphore.acquire()
         displayElements[motePort]["destination_fields"]["address_field"].config(background="red")
         tkSemaphore.release()
         return_value = False
   else:
      tkSemaphore.acquire()
      displayElements[motePort]["destination_fields"]["address_field"].config(background="red")
      tkSemaphore.release()
      return_value = False
   if port.isdigit():
      tkSemaphore.acquire()
      displayElements[motePort]["destination_fields"]["port_field"].config(background="green")
      tkSemaphore.release()
   else:
      tkSemaphore.acquire()
      displayElements[motePort]["destination_fields"]["port_field"].config(background="red")
      tkSemaphore.release()
      return_value = False
   return return_value

def retrieveDestinationAddress(motePort):
   tkSemaphore.acquire()
   address = displayElements[motePort]["destination_fields"]["address_string"].get()
   tkSemaphore.release()
   return_value = ''
   for i in range(0,16):
      return_value += chr(int(address[2*i:2*i+2],16))
   return return_value

def retrieveDestinationPort(motePort):
   tkSemaphore.acquire()
   port = int(displayElements[motePort]["destination_fields"]["port_string"].get())
   tkSemaphore.release()
   return_value  = chr(int(port/256))
   return_value += chr(    port%256)
   return return_value
   
#============================ GUI functions ===================================

def showDetails():
   rowCounter=0;
   tkSemaphore.acquire()
   for key,value in displayElements.iteritems():
      if (value["CheckbuttonVar"].get()):
         value["moteFrame"].grid(row=rowCounter,column=1)
         rowCounter = rowCounter+1
      else:
         value["moteFrame"].grid_forget()
   tkSemaphore.release()

def errorTextHeader():
   errorText.insert(Tkinter.END,datetime.datetime.now().strftime("%H:%M:%S")+" ")

class SemaphoreEnabledScrollbar(Tkinter.Scrollbar):
   def set(self, *args):
      tkSemaphore.acquire()
      Tkinter.Scrollbar.set(self, *args)
      tkSemaphore.release()

class SemaphoreEnabledText(Tkinter.Text):
    def yview(self, *args):
        tkSemaphore.acquire()
        Tkinter.Text.yview(self, *args)
        tkSemaphore.release()

def clearErrorText():
   tkSemaphore.acquire()
   errorText.delete(1.0,Tkinter.END)
   tkSemaphore.release()

def releaseAndQuit():
   root.quit()
   sys.exit()

def printError(errorString):
   if debugOpenDisplay==True:
      print '[OpenDisplay] printError'
   try:
      tkSemaphore.acquire()
      errorTextHeader()
      errorText.insert(Tkinter.END,errorString+"\n")
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error printError: %s (%s) \n" % (str(err[0]), str(err[1])))

def clearLatestUpdate(motePort):
   tkSemaphore.acquire()
   displayElements[motePort]["IDManager"].config(bg=color["updatedOld"])
   displayElements[motePort]["myDAGrank"].config(bg=color["updatedOld"])
   displayElements[motePort]["outputBuffer"].config(bg=color["updatedOld"])
   displayElements[motePort]["asn"].config(bg=color["updatedOld"])
   displayElements[motePort]["macStats"].config(bg=color["updatedOld"])
   displayElements[motePort]["schedule"]["frame"].config(bg=color["updatedOld"])
   displayElements[motePort]["queue"]["frame"].config(bg=color["updatedOld"])
   displayElements[motePort]["neighbors"]["frame"].config(bg=color["updatedOld"])
   tkSemaphore.release()

#============================ graph ===========================================

def redrawGraph():
   for key,value in openRecord.recordElements.iteritems():
      try:
         if str(value["addr_16b"]) in moteLocation.keys():
            tkSemaphore.acquire()
            displayElements[key]["location"]=moteLocation[str(value["addr_16b"])]
            tkSemaphore.release()
         else:
            tkSemaphore.acquire()
            displayElements[key]["location"]=(random.randint(0,GRAPHSIZEWIDTH),random.randint(0,GRAPHSIZEHEIGHT))
            tkSemaphore.release()
      except:
         return
   tkSemaphore.acquire()
   graphCanvas.addtag_all("removeMe")
   graphCanvas.dtag(backgroundImage,"removeMe")
   graphCanvas.delete("redraw")
   # for each of the motes in the network
   for motePort,value in displayElements.iteritems():
      #get the mote's location
      x,y=displayElements[motePort]["location"]
      try:
         for key,neighbor in openRecord.recordElements[motePort]["neighbors"]["contentRows"].iteritems():
            #go over the mote's neighbors
            if neighbor["used"]==1:
               #find the neighbor's motePort
               for motePort_neighbor,value_neighbor in displayElements.iteritems():
                  if openRecord.recordElements[motePort_neighbor]["addr_16b"]==neighbor["addr_16b"]:
                     #find the neighbor's location
                     xneighbor,yneighbor=displayElements[motePort_neighbor]["location"]
                     #draw the neighbor links
                     temp_tag= "link"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"+str(neighbor["addr_16b"])
                     temp_elems = graphCanvas.find_withtag(temp_tag)
                     if (len(temp_elems)==0):
                        graphCanvas.create_line(x,y,(x+xneighbor)/2,(y+yneighbor)/2,
                              fill=color["unstableneighbor"],width=1,tags=temp_tag)
                     else:
                        graphCanvas.dtag(temp_elems[0],"removeMe")
                     #draw the parentPreference links
                     if neighbor["parentPreference"]:
                        temp_tag= "stableParent"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"+\
                              str(neighbor["addr_16b"])
                        temp_elems = graphCanvas.find_withtag(temp_tag)
                        if (len(temp_elems)==0):
                           graphCanvas.create_line(x,y,x+(xneighbor-x)/3,y+(yneighbor-y)/3,
                              fill=color["stableneighbor"],arrow=Tkinter.LAST,width=3,tags=temp_tag)
                        else:
                           graphCanvas.dtag(temp_elems[0],"removeMe")
                     #draw the stableNeighbor links
                     elif neighbor["stableNeighbor"]:
                        temp_tag= "stableNeighbor"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"+\
                              str(neighbor["addr_16b"])
                        temp_elems = graphCanvas.find_withtag(temp_tag)
                        if (len(temp_elems)==0):
                           graphCanvas.create_line(x,y,x+(xneighbor-x)/3,y+(yneighbor-y)/3,
                              fill=color["stableneighbor"],arrow=Tkinter.NONE,width=3,tags=temp_tag)
                        else:
                           graphCanvas.dtag(temp_elems[0],"removeMe")                        
                     else:
                        graphCanvas.create_line(x,y,
                              x+(float(neighbor["switchStabilityCounter"])/float(SWITCHSTABILITYTHRESHOLD))*(xneighbor-x)/3,
                              y+(float(neighbor["switchStabilityCounter"])/float(SWITCHSTABILITYTHRESHOLD))*(yneighbor-y)/3,
                              fill=color["unstableneighbor"],arrow=Tkinter.NONE,width=5,tags="redraw")
                     #draw the scheduled slot links
                     try:
                        for key,scheduledslot in openRecord.recordElements[motePort]["schedule"]["contentRows"].iteritems():
                           if (scheduledslot["type"]=="TXDAT" and scheduledslot["neighbor"]==neighbor["addr_16b"]):
                              if (scheduledslot["primary"]):
                                 temp_tag= "txLinkP"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"+\
                                       str(neighbor["addr_16b"])
                                 temp_elems = graphCanvas.find_withtag(temp_tag)
                                 if (len(temp_elems)==0):
                                    graphCanvas.create_line(x+(xneighbor-x)/6,y+(yneighbor-y)/6,
                                          x+3*(xneighbor-x)/12,y+3*(yneighbor-y)/12,
                                          fill=color["scheduledSlotP"],arrow=LAST,width=4,tags=temp_tag)
                                 else:
                                    graphCanvas.dtag(temp_elems[0],"removeMe")
                              else:
                                 temp_tag= "txLinkS"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"+\
                                       str(neighbor["addr_16b"])
                                 temp_elems = graphCanvas.find_withtag(temp_tag)
                                 if (len(temp_elems)==0):
                                    graphCanvas.create_line(x+(xneighbor-x)/6,y+(yneighbor-y)/6,
                                          x+3*(xneighbor-x)/12,y+3*(yneighbor-y)/12,
                                          fill=color["scheduledSlotS"],arrow=LAST,width=4,tags=temp_tag)
                                 else:
                                    graphCanvas.dtag(temp_elems[0],"removeMe")
                           if (scheduledslot["type"]=="RXDAT" and scheduledslot["neighbor"]==neighbor["addr_16b"]):
                              if (scheduledslot["primary"]):
                                 temp_tag= "rxLinkP"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"+\
                                       str(neighbor["addr_16b"])
                                 temp_elems = graphCanvas.find_withtag(temp_tag)
                                 if (len(temp_elems)==0):
                                    graphCanvas.create_line(x+(xneighbor-x)/6,y+(yneighbor-y)/6,
                                          x+1*(xneighbor-x)/12,y+1*(yneighbor-y)/12,
                                          fill=color["scheduledSlotP"],arrow=LAST,width=4,tags=temp_tag)
                                 else:
                                    graphCanvas.dtag(temp_elems[0],"removeMe")
                              else:
                                 temp_tag= "rxLinkS"+"from"+str(openRecord.recordElements[motePort]["addr_16b"])+"to"\
                                       +str(neighbor["addr_16b"])
                                 temp_elems = graphCanvas.find_withtag(temp_tag)
                                 if (len(temp_elems)==0):
                                    graphCanvas.create_line(x+(xneighbor-x)/6,y+(yneighbor-y)/6,
                                          x+1*(xneighbor-x)/12,y+1*(yneighbor-y)/12,
                                          fill=color["scheduledSlotS"],arrow=LAST,width=4,tags=temp_tag)
                                 else:
                                    graphCanvas.dtag(temp_elems[0],"removeMe")
                     except KeyError: #openRecord.recordElements[motePort]["schedule"]["contentRows"] empty
                        pass
      except KeyError:
         pass #openRecord.recordElements[motePort]["neighbors"]["contentRows"] empty
      try:
         if (openRecord.recordElements[motePort]["isDAGroot"]==1):
            #draw the DAGroot
            temp_tag= "DAGroot"+str(openRecord.recordElements[motePort]["addr_16b"])
            temp_elems = graphCanvas.find_withtag(temp_tag)
            if (len(temp_elems)==0):   
               graphCanvas.create_rectangle(x-GRAPHMOTESIZE/2,y-GRAPHMOTESIZE/2,
                                       x+GRAPHMOTESIZE/2,y+GRAPHMOTESIZE/2,
                                       fill=color["mote"],activefill='red',tags=temp_tag)
            else:
               graphCanvas.dtag(temp_elems[0],"removeMe")
            #draw the DAGroot label
            temp_tag= "DAGrootLabel"+str(openRecord.recordElements[motePort]["addr_16b"])
            temp_elems = graphCanvas.find_withtag(temp_tag)
            if (len(temp_elems)==0):
               graphCanvas.create_text(x,y,text=openRecord.recordElements[motePort]["addr_16b"],tags=temp_tag)
            else:
               graphCanvas.dtag(temp_elems[0],"removeMe")
         else:
            #draw the mote
            temp_tag= "mote"+str(openRecord.recordElements[motePort]["addr_16b"])
            temp_elems = graphCanvas.find_withtag(temp_tag)
            if (len(temp_elems)==0):   
               graphCanvas.create_oval(x-GRAPHMOTESIZE/2,y-GRAPHMOTESIZE/2,
                                       x+GRAPHMOTESIZE/2,y+GRAPHMOTESIZE/2,
                                       fill=color["mote"],activefill='red',tags=temp_tag)
            else:
               graphCanvas.dtag(temp_elems[0],"removeMe")
            #draw the mote label
            temp_tag= "moteLabel"+str(openRecord.recordElements[motePort]["addr_16b"])
            temp_elems = graphCanvas.find_withtag(temp_tag)
            if (len(temp_elems)==0):
               graphCanvas.create_text(x,y,text=openRecord.recordElements[motePort]["addr_16b"],tags=temp_tag)
            else:
               graphCanvas.dtag(temp_elems[0],"removeMe")
         #draw the mote DAGrank
         temp_tag= "DAGrank"+str(openRecord.recordElements[motePort]["addr_16b"])+"is"+\
               str(openRecord.recordElements[motePort]["myDAGrank"])
         temp_elems = graphCanvas.find_withtag(temp_tag)
         if (len(temp_elems)==0):
            graphCanvas.create_text(x,y+15,text=str(openRecord.recordElements[motePort]["myDAGrank"]),tags=temp_tag)
         else:
            graphCanvas.dtag(temp_elems[0],"removeMe")
      except KeyError:
         pass #openRecord.recordElements[motePort]["neighbors"]["contentRows"] empty
   graphCanvas.delete("removeMe")
   tkSemaphore.release()

#============================ display =========================================

def displayID(motePort):
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["Checkbutton"].config(text=str(openRecord.recordElements[motePort]["addr_16b"]))
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayID: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayIsSync(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayIsSync'
   # pick the color
   if openRecord.recordElements[motePort]["isSync"]==1:
      syncColor=color["isSynced"]
   else:
      syncColor=color["isNotSynced"]
   # color the frame
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["moteFrame"].config(bg=syncColor)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayIsSync: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayIDManager(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayIDManager'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["IDManager"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   try:
      outputtext  = "isDAGroot="  + str(openRecord.recordElements[motePort]["isDAGroot"])
      outputtext += "\nisBridge=" + str(openRecord.recordElements[motePort]["isBridge"])
      outputtext += "\nmy16bID="  + str(openRecord.recordElements[motePort]["my16bID"])
      outputtext += "\nmy64bID="  + str(openRecord.recordElements[motePort]["my64bID"])
      outputtext += "\nmyPANID="  + str(openRecord.recordElements[motePort]["myPANID"])
      outputtext += "\nmyPrefix=" + str(openRecord.recordElements[motePort]["myPrefix"])
      tkSemaphore.acquire()
      displayElements[motePort]["IDManager"].config(text=outputtext)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayIDManager: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayMyDAGrank(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayMyDAGrank'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["myDAGrank"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["myDAGrank"].config(text="myDAGrank="+str(openRecord.recordElements[motePort]["myDAGrank"]))
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayMyDAGrank: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayOutputBuffer(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayOutputBuffer'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["outputBuffer"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   output ="w="+str(openRecord.recordElements[motePort]["output_buffer_index_write"])+"\n"
   output+="r=" +str(openRecord.recordElements[motePort]["output_buffer_index_read"] )+"\n"
   output+="occupied="+str((openRecord.recordElements[motePort]["output_buffer_index_write"]-\
         openRecord.recordElements[motePort]["output_buffer_index_read"])%300)
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["outputBuffer"].config(text=output)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayOutputBuffer: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayAsn(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayAsn'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["asn"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["asn"].config(text="asn="+str(openRecord.recordElements[motePort]["asn"]))
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayAsn: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayMacStats(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayMacStats'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["macStats"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   try:
      outputtext  = "syncCounter="     + str(openRecord.recordElements[motePort]["syncCounter"])
      if (openRecord.recordElements[motePort]["syncCounter"]!=0):
         outputtext += "\nminCorrection=" + str(openRecord.recordElements[motePort]["minCorrection"]*30) + " us"
         outputtext += "\nmaxCorrection=" + str(openRecord.recordElements[motePort]["maxCorrection"]*30) + " us"
      outputtext += "\nnumDeSync="     + str(openRecord.recordElements[motePort]["numDeSync"])
      tkSemaphore.acquire()
      displayElements[motePort]["macStats"].config(text=outputtext)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayMacStats: %s (%s) \n" % (str(err[0]), str(err[1])))

def displaySchedule(motePort,last_row):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displaySchedule'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["schedule"]["frame"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   # format the schedule
   output = "type | channel | neighbor | numRx | numTx | numACK | cost | asn"
   for key, value in openRecord.recordElements[motePort]["schedule"]["contentRows"].iteritems():
      #if (value["type"]!="OFF"):
      if (True):
         output += '\n'
         output +=   str(key)
         output +=" | "+str(value["type"])
         if value["shared"]==1:
            output +=" S(2^"+str(value["backoffExponent"])+"->"+str(value["backoff"])+")"
         output +=" | "+str(value["channelOffset"])
         output +=" | "+value["neighbor"]
         output +=" | "+str(value["numRx"])
         output +=" | "+str(value["numTx"])
         output +=" | "+str(value["numTxACK"])
         output +=" | "+str(value["cost"])
         output +=" | "+str(value["asn"])
         if value["asn"]!=0:
            output+=" (%.2f"%((openRecord.recordElements[motePort]["asn"]-value["asn"])/100.0)+"s)"
   # display the schedule
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["schedule"]["Table"].config(text=output)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displaySchedule 1: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayQueue(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayQueue'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["queue"]["frame"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   # create the table contents
   output = "# | creator | owner"
   for key, value in openRecord.recordElements[motePort]["queue"]["contentRows"].iteritems():
      if (value["owner"]=="COMPONENT_NULL"):
         output += "\n"+str(key)+" | - | - "
      else:
         output += "\n"+str(key)+" | "+str(value["creator"].strip('COMPONENT_'))+" | "+str(value["owner"].strip('COMPONENT_'))
   # display table
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["queue"]["Table"].config(text=output)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayQueue 1: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayNeighbors(motePort,last_row):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayNeighbors'
   # highlight the latest updated field
   clearLatestUpdate(motePort)
   tkSemaphore.acquire()
   displayElements[motePort]["neighbors"]["frame"].config(bg=color["updatedLatest"])
   tkSemaphore.release()
   # build table string
   output = "# | P | N | id | DAGr. | rssi | numRx | numTx | numACK | cost | asn"
   for key, value in openRecord.recordElements[motePort]["neighbors"]["contentRows"].iteritems():
      if (value["used"]==1):
         # row number (#)
         output += '\n'+str(key)
         # parent preference (P)
         if (value["parentPreference"]):
            output+=" | X"
         else :
            output+=" | "
         # stable neighbor
         if (value["stableNeighbor"]):
            output+=" | X"
         else :
            output+=" | "
         output+="("+str(value["switchStabilityCounter"])+")"
         # id
         output+=" | "+hex(value["addr_64b"])
         # DAG rank
         output+=" | "+str(value["DAGrank"])
         # rssi
         output+=" | "+str(value["rssi"])
         # num Rx
         output+=" | "+str(value["numRx"])
         # num Tx
         output+=" | "+str(value["numTx"])
         # num Tx with ACK
         output+=" | "+str(value["numTxACK"])
         # cost
         output+=" | "+str(value["cost"])
         # asn
         output+=" | "+str(value["asn"])
         output+=" (%.2f"%((openRecord.recordElements[motePort]["asn"]-value["asn"])/100.0)+"s)"
   # print table
   try:
      tkSemaphore.acquire()
      displayElements[motePort]["neighbors"]["Table"].config(text=output)
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayNeighbors 1: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayError(motePort,errorString,seriousness):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayError'
   try:
      tkSemaphore.acquire()
      errorTextHeader()
      errorText.insert(Tkinter.END,errorString,(motePort,seriousness))
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayError: %s (%s) \n" % (str(err[0]), str(err[1])))

def displayData(motePort):
   # print debug message
   if debugOpenDisplay==True:
      print '[OpenDisplay] displayData'
   output ="["+str(openRecord.recordElements[motePort]["addr_16b"]  )+"] data\n"
   try:
      tkSemaphore.acquire()
      errorTextHeader()
      errorText.insert(Tkinter.END,output, (motePort))
      tkSemaphore.release()
   except:
      err = sys.exc_info()
      sys.stderr.write( "Error displayData: %s (%s) \n" % (str(err[0]), str(err[1])))

#============================ start GUI =======================================

def startGUI():
   root.mainloop()

#============================ "main" ==========================================

root=Tkinter.Tk()
root.title("OpenVisualizer")
root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
root.resizable(0,0)

print 'loading location '+location+'...'
if   (location=='joppa'):
   GRAPHSIZEWIDTH  = GRAPHSIZE_JOPPA_WIDTH
   GRAPHSIZEHEIGHT = GRAPHSIZE_JOPPA_HEIGHT
   map = Tkinter.PhotoImage(file="joppa.gif")
   moteLocation = moteLocationJoppa
elif (location=='cory471'):
   GRAPHSIZEWIDTH  = GRAPHSIZE_471
   GRAPHSIZEHEIGHT = GRAPHSIZE_471
   map = Tkinter.PhotoImage(file="471cory.gif")
   moteLocation = moteLocationCory471
else:
   GRAPHSIZEWIDTH  = GRAPHSIZE_DEFAULT
   GRAPHSIZEHEIGHT = GRAPHSIZE_DEFAULT
   map = Tkinter.PhotoImage()
   moteLocation = moteLocationDefault

#===== left frame
leftFrame       = Tkinter.Frame(root,borderwidth=0)
leftFrame.grid(row=0,column=0)
#--- check buttons
showDetailButtonFrame = Tkinter.Frame(leftFrame,borderwidth=0,relief=Tkinter.SUNKEN)
showDetailButtonFrame.grid(row=0)
#--- graph
graphCanvas     = Tkinter.Canvas(leftFrame,width=GRAPHSIZEWIDTH,height=GRAPHSIZEHEIGHT,background='white')
backgroundImage = graphCanvas.create_image(0,0,image=map,anchor=Tkinter.NW)
graphCanvas.grid(row=1)
#--- redraw button
redrawButton   = Tkinter.Button(leftFrame,text="Redraw Topology",command=redrawGraph)
redrawButton.grid(row=2)
#--- errorText
errorTextFrame = Tkinter.Frame(leftFrame,borderwidth=0)
scrollbar = SemaphoreEnabledScrollbar(errorTextFrame)
errorText = SemaphoreEnabledText(errorTextFrame,height=TEXTHEIGHT,width=TEXTWIDTH,wrap=Tkinter.WORD,yscrollcommand=scrollbar.set)
errorText.tag_config("error",            background="#FFD4FF" )
errorText.tag_config("warning",          background="#AAFFFF" )
errorText.tag_config("debug",            background="#D4FFD4" )
errorText.tag_config("tempDebug",        background="#00FF00" )
errorText.tag_config("keepConnectivity", background="#F5F5F5" )
scrollbar.config(command=errorText.yview)
scrollbar.grid(row=1,column=1,sticky=Tkinter.N+Tkinter.S)
errorText.grid(row=1,column=0)
errorTextFrame.grid(row=3)
#--- clear button
clearButton     = Tkinter.Button(leftFrame,text="Clear Errors",command=clearErrorText)
clearButton.grid(row=4)
#--- lbr connection frame
shared.lbrFrame        = Tkinter.Frame(leftFrame,borderwidth=0)
shared.lbrFrame.grid(row=5)
#===== right frame
rightFrame      = Tkinter.Frame(root,borderwidth=0,relief=Tkinter.SUNKEN)
rightFrame.grid(row=0,column=1)
