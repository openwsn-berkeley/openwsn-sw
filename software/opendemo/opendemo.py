import socket
import binascii
import time
import os
import Tkinter
import sys
import threading
import datetime
import serial
if os.name=='nt':
   import _winreg as winreg

ihaveamac            = 0     #set to 1 if you have a mac computer

myAddress            = ''    # means 'any suitable interface'

IPV6PREFIX   = '2001:0470:846d:1'
IP64B_PREFIX = ''.join(['\x20','\x01','\x04','\x70','\x84','\x6d','\x00','\x01'])

#the ports the GINA mote is listening on
WKP_GINA_UDP_ECHO     =    7
WKP_GINA_UDP_LED      = 2193
WKP_GINA_UDP_GINA     = 2190
WKP_GINA_UDP_HELI     = 2192
WKP_GINA_UDP_WARPWING = 2194
#the ports this script is listening on
WKP_SCRIPT_UDP_ECHO     = 8087
WKP_SCRIPT_UDP_LED      = 8085
WKP_SCRIPT_UDP_GINA     = 8080
WKP_SCRIPT_UDP_HELI     = 8082
WKP_SCRIPT_UDP_WARPWING = 8081
WKP_PROXY_CLIENT        = 8899
WKP_PROXY_SERVER        = 7788

serialHandler      = ''

dataToSend         = ''
dataToSendLock     = threading.Lock()
commandToSend      = ''
commandToSendLock  = threading.Lock()
guiLock            = threading.Lock()

#================================= retrieve stored configuration ====

try:
   file = open('saved_opendemo_settings.dat', 'r')
   default_connectionAddress = file.readline()
   default_connectionAddress = default_connectionAddress[:len(default_connectionAddress)-1]
   default_proxyAddress      = file.readline()
   file.close()
except:
   print "No saved configuration."
   default_connectionAddress = '2001:470:846d:1:1415:9209:22b:51'
   default_proxyAddress      = '128.32.33.233'   
else:
   output  = ''
   output += "saved config:"
   output += "\n- default_connectionAddress = "+default_connectionAddress
   output += "\n- default_proxyAddress = "     +default_proxyAddress
   print output

#================================= GUI definition ===================

def releaseAndQuit():
   global disable_bridge, socketThreads_active, moteThread_active
   disable_bridge=1
   time.sleep(.2)
   socketThreads_active=0
   time.sleep(.2)
   moteThread_active=0
   time.sleep(.2)
   print 'GUI exiting.'
   root.quit()
   sys.exit()

def save_config():
   global guiLock
   guiLock.acquire()
   connectionAddress_config = connectionAddress.get(1.0,Tkinter.END)
   connectionAddress_config = connectionAddress_config[:len(connectionAddress_config)-1]
   proxyAddress_config      = proxyAddress.get(1.0,Tkinter.END)
   proxyAddress_config      = proxyAddress_config[:len(proxyAddress_config)-1]
   guiLock.release()
   output  = ''
   output += "\nstoring config:"
   output += "\n- connectionAddress_config="+connectionAddress_config
   output += "\n- proxyAddress_config="     +proxyAddress_config +"\n"
   print output
   file = open('saved_opendemo_settings.dat', 'w')
   file.write(connectionAddress_config+"\n"+proxyAddress_config)
   file.close()

def gui_key_pressed(event):
   if (event.char=='o'):
      url_clicked(event)
   if (choiceText.get()=="heli"):
      if (event.char=='i'):
         heli_up()
      if (event.char=='j'):
         heli_left()
      if (event.char=='l'):
         heli_right()
      if (event.char=='k'):
         heli_down()
      if (event.char==' '):
         heli_stop()
      if (event.char=='q'):
         heli_takeoff()
      if (event.char=='a'):
         heli_land()

def openChoice():
   global guiLock
   guiLock.acquire()
   if (choiceText.get()=="udpEcho"):
      udpEchoFrame.grid(row=0,column=0)
      udpLedFrame.grid_forget()
      imuFrame.grid_forget()
      heliFrame.grid_forget()
      warpwingFrame.grid_forget()
   if (choiceText.get()=="udpLed"):
      udpEchoFrame.grid_forget()
      udpLedFrame.grid(row=1,column=0)
      imuFrame.grid_forget()
      heliFrame.grid_forget()
      warpwingFrame.grid_forget()
   if (choiceText.get()=="imu"):
      udpEchoFrame.grid_forget()
      udpLedFrame.grid_forget()
      imuFrame.grid(row=2,column=0)
      heliFrame.grid_forget()
      warpwingFrame.grid_forget()
   if (choiceText.get()=="heli"):
      udpEchoFrame.grid_forget()
      udpLedFrame.grid_forget()
      imuFrame.grid_forget()
      heliFrame.grid(row=3,column=0)
      warpwingFrame.grid_forget()
   if (choiceText.get()=="warpwing"):
      udpEchoFrame.grid_forget()
      udpLedFrame.grid_forget()
      imuFrame.grid_forget()
      heliFrame.grid_forget()
      warpwingFrame.grid(row=4,column=0)
   guiLock.release()

root=Tkinter.Tk()
root.title("OpenWSN")
root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
root.resizable(0,0)

root.bind("<Key>",gui_key_pressed)

#================================================ leftFrame

leftFrame = Tkinter.Frame(root,borderwidth=1,relief=Tkinter.SUNKEN,padx=10,pady=10)

#==================== connectionFrame

connectionFrame = Tkinter.Frame(leftFrame)

temp = Tkinter.Label(connectionFrame, text="Your mote's IPv6 address:")
temp.grid(row=0,column=0,columnspan=3,sticky=Tkinter.W)

connectionAddress = Tkinter.Text(connectionFrame,width=35,height=1)
connectionAddress.insert(Tkinter.END,default_connectionAddress)
connectionAddress.grid(row=1,column=0,columnspan=3)

connectionType = Tkinter.StringVar()
connectionType.set("basestation")
temp = Tkinter.Radiobutton(connectionFrame, text="basestation", variable=connectionType, value="basestation")
temp.grid(row=2,column=0)
temp = Tkinter.Radiobutton(connectionFrame, text="IPv6",        variable=connectionType, value="IPv6")
temp.grid(row=2,column=1)
temp = Tkinter.Radiobutton(connectionFrame, text="IPv4",        variable=connectionType, value="IPv4")
temp.grid(row=2,column=2)

temp = Tkinter.Label(connectionFrame, text="proxy's IPv4 address:")
temp.grid(row=3,column=0,columnspan=3,sticky=Tkinter.W)

proxyAddress = Tkinter.Text(connectionFrame,width=35,height=1)
proxyAddress.insert(Tkinter.END,default_proxyAddress)
proxyAddress.grid(row=4,column=0,columnspan=3)

temp = Tkinter.Button(connectionFrame, text="save", command=save_config)
temp.grid(row=5,column=0,columnspan=3,sticky=Tkinter.E)

#==================== connectionCanvas

connectionCanvas = Tkinter.Canvas(connectionFrame,width=200,height=150)
temp_y  = 10
connectionCanvas.create_text( 70,temp_y  ,text="basestation connected?",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="basestation_connected_led")
connectionCanvas.create_text(185,temp_y  ,text="",justify=Tkinter.LEFT,tag="basestation_connected_text")
temp_y += 20
connectionCanvas.create_text( 65,temp_y  ,text="status from basestation",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="status_from_basestation_led",fill="")
connectionCanvas.create_oval(165,temp_y-5,175,temp_y+5,tag="status_from_basestation_led",fill="")
temp_y += 20
connectionCanvas.create_text( 70,temp_y  ,text="request from basestation",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="request_from_basestation_led",fill="")
connectionCanvas.create_oval(165,temp_y-5,175,temp_y+5,tag="request_from_basestation_led",fill="")
temp_y += 20
connectionCanvas.create_text( 65,temp_y  ,text="data from basestation",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="data_from_basestation_led",fill="")
connectionCanvas.create_oval(165,temp_y-5,175,temp_y+5,tag="data_from_basestation_led",fill="")
temp_y += 20
connectionCanvas.create_text( 65,temp_y  ,text="error from basestation",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="error_from_basestation_led",fill="")
connectionCanvas.create_oval(165,temp_y-5,175,temp_y+5,tag="error_from_basestation_led",fill="")
temp_y += 20
connectionCanvas.create_text( 65,temp_y  ,text="pending data to send",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="pending_data_led")
temp_y += 20
connectionCanvas.create_text( 75,temp_y  ,text="pending command to send",justify=Tkinter.LEFT)
connectionCanvas.create_oval(150,temp_y-5,160,temp_y+5,tag="pending_command_led")
connectionCanvas.grid(row=6,column=0,columnspan=3)

connectionFrame.grid(row=0,column=0)

#==================== choiceFrame

choiceFrame = Tkinter.Frame(leftFrame,borderwidth=1,relief=Tkinter.RAISED)

choiceText = Tkinter.StringVar()
temp=Tkinter.Radiobutton(choiceFrame,text="Inertial Measurements (Part IV)",variable=choiceText,value="imu"    ,command=openChoice)
temp.grid(row=0,column=0,sticky=Tkinter.W)
temp=Tkinter.Radiobutton(choiceFrame,text="UDP Led (Part V)"               ,variable=choiceText,value="udpLed" ,command=openChoice)
temp.grid(row=1,column=0,sticky=Tkinter.W)
temp=Tkinter.Radiobutton(choiceFrame,text="UDP Echo (Part VI)"             ,variable=choiceText,value="udpEcho",command=openChoice)
temp.grid(row=2,column=0,sticky=Tkinter.W)
temp=Tkinter.Radiobutton(choiceFrame,text="Helicopter Control (Part VII)"  ,variable=choiceText,value="heli"   ,command=openChoice)
temp.grid(row=3,column=0,sticky=Tkinter.W)
temp=Tkinter.Radiobutton(choiceFrame,text="WARPWING data"                  ,variable=choiceText,value="warpwing",command=openChoice)
temp.grid(row=4,column=0,sticky=Tkinter.W)

choiceFrame.grid(row=1,column=0,columnspan=3)

#==================== infoFrame

def url_clicked(event):
   os.startfile('http://openwsn.berkeley.edu/')

infoFrame = Tkinter.Frame(leftFrame,pady=10)
temp = Tkinter.Label(infoFrame,text="Workshop's webpage <o>")
temp.bind("<Button-1>",url_clicked)
temp.bind("<Button-2>",url_clicked)
temp.bind("<Button-3>",url_clicked)
temp.grid(row=0,column=1)
infoFrame.grid(row=2,column=0,columnspan=3)

leftFrame.grid(row=0,column=0)

#================================================ rightFrame

rightFrame = Tkinter.Frame(root,padx=10,pady=10)

#-------------------- imu functions

def imu_send():
   global imuChoices, guiLock
   try:
      guiLock.acquire()
      num_measurements = imuChoices['num_measurements'].get(1.0,Tkinter.END)
      guiLock.release()
      num_measurements = int(num_measurements)
   except:
      guiLock.acquire()
      imuChoices['num_measurements'].config(background="red")
      guiLock.release()
   else:
      guiLock.acquire()
      imuChoices['num_measurements'].config(background="green")
      guiLock.release()
      udp_proxy_send(str(chr(num_measurements)),WKP_SCRIPT_UDP_GINA,WKP_GINA_UDP_GINA)

def imu_receive(received_payload):
   global imuReplyLabel, imuCanvas, guiLock
   #calculate measurements values in native units
   measurements = {}
   measurements['sensitive_accel_x' ]  = {}
   measurements['sensitive_accel_x' ] ['hex'] = binascii.hexlify(received_payload[ 0: 2])
   measurements['sensitive_accel_x' ] ['dec'] = int(256*ord(received_payload[0])+ord(received_payload[ 1]))
   measurements['sensitive_accel_x' ] ['v']   = (float(measurements['sensitive_accel_x']['dec'])/2**12)*3.0
   measurements['sensitive_accel_x' ] ['G']   = -(measurements['sensitive_accel_x']['v']-1.5)/0.6
   measurements['sensitive_accel_y' ]  = {}
   measurements['sensitive_accel_y' ] ['hex'] = binascii.hexlify(received_payload[ 2: 4])
   measurements['sensitive_accel_y' ] ['dec'] = int(256*ord(received_payload[ 2])+ord(received_payload[ 3]))
   measurements['sensitive_accel_y' ] ['v']   = (float(measurements['sensitive_accel_y']['dec'])/2**12)*3.0
   measurements['sensitive_accel_y' ] ['G']   = -(measurements['sensitive_accel_y']['v']-1.5)/0.6
   measurements['sensitive_accel_z1']  = {}
   measurements['sensitive_accel_z1'] ['hex'] = binascii.hexlify(received_payload[ 4: 6])
   measurements['sensitive_accel_z1'] ['dec'] = int(256*ord(received_payload[ 4])+ord(received_payload[ 5]))
   measurements['sensitive_accel_z1'] ['v']   = (float(measurements['sensitive_accel_z1']['dec'])/2**12)*3.0
   measurements['sensitive_accel_z1'] ['G']   = -(measurements['sensitive_accel_z1']['v']-1.5)/0.6
   measurements['sensitive_accel_z3']  = {}
   measurements['sensitive_accel_z3'] ['hex'] = binascii.hexlify(received_payload[ 6: 8])
   measurements['sensitive_accel_z3'] ['dec'] = int(256*ord(received_payload[ 6])+ord(received_payload[ 7]))
   measurements['sensitive_accel_z3'] ['v']   = (float(measurements['sensitive_accel_z3']['dec'])/2**12)*3.0
   measurements['sensitive_accel_z3'] ['G']   = -(measurements['sensitive_accel_z3']['v']-1.5)/0.6
   measurements['temperature']         = {}
   measurements['temperature']        ['hex'] = binascii.hexlify(received_payload[ 8:10])
   measurements['temperature' ]       ['dec'] = int(256*ord(received_payload[ 8])+ord(received_payload[ 9]))
   measurements['temperature']        ['v']   = (float(measurements['temperature']['dec'])/2**12)*3.0
   measurements['temperature']        ['C']   = 160.74-(86.237*measurements['temperature']['v'])
   measurements['magnetometer_x']      = {}
   measurements['magnetometer_x']     ['hex'] = binascii.hexlify(received_payload[10:12])
   measurements['magnetometer_x']     ['dec'] = int(measurements['magnetometer_x']['hex'],16)
   if (measurements['magnetometer_x'] ['dec']>>15==1):
      measurements['magnetometer_x' ] ['dec']-= 1<<16
   measurements['magnetometer_x']     ['Ga']  =     measurements['magnetometer_x']['dec']/970.0
   measurements['magnetometer_y']      = {}
   measurements['magnetometer_y']     ['hex'] = binascii.hexlify(received_payload[12:14])
   measurements['magnetometer_y']     ['dec'] = int(measurements['magnetometer_y']['hex'],16)
   if (measurements['magnetometer_y'] ['dec']>>15==1):
      measurements['magnetometer_y' ] ['dec']-= 1<<16
   measurements['magnetometer_y']     ['Ga']  =     measurements['magnetometer_y']['dec']/970.0
   measurements['magnetometer_z']      = {}
   measurements['magnetometer_z']     ['hex'] = binascii.hexlify(received_payload[14:16])
   measurements['magnetometer_z']     ['dec'] = int(measurements['magnetometer_z']['hex'],16)
   if (measurements['magnetometer_z'] ['dec']>>15==1):
      measurements['magnetometer_z' ] ['dec']-= 1<<16
   measurements['magnetometer_z']     ['Ga']  =     measurements['magnetometer_z']['dec']/970.0
   measurements['large_range_accel_x'] = {}
   measurements['large_range_accel_x']['hex'] = binascii.hexlify(received_payload[16:18])
   measurements['large_range_accel_x']['dec'] = int(measurements['large_range_accel_x']['hex'],16)>>4
   measurements['large_range_accel_x']['G']   = -(float(measurements['large_range_accel_x']['dec'])-2130.0)/205.0
   measurements['large_range_accel_y'] = {}
   measurements['large_range_accel_y']['hex'] = binascii.hexlify(received_payload[18:20])
   measurements['large_range_accel_y']['dec'] = int(measurements['large_range_accel_y']['hex'],16)>>4
   measurements['large_range_accel_y']['G']   = -(float(measurements['large_range_accel_y']['dec'])-2130.0)/205.0
   measurements['large_range_accel_z'] = {}
   measurements['large_range_accel_z']['hex'] = binascii.hexlify(received_payload[20:22])
   measurements['large_range_accel_z']['dec'] = int(measurements['large_range_accel_z']['hex'],16)>>4
   measurements['large_range_accel_z']['G']   = -(float(measurements['large_range_accel_z']['dec'])-2130.0)/205.0
   measurements['gyro_temperature']    = {}
   measurements['gyro_temperature']   ['hex'] = binascii.hexlify(received_payload[22:24])
   measurements['gyro_x']              = {}
   measurements['gyro_x']             ['hex'] = binascii.hexlify(received_payload[24:26])
   measurements['gyro_x']             ['dec'] = int(measurements['gyro_x']['hex'],16)
   if (measurements['gyro_x']['dec']>>15==1):
      measurements['gyro_x' ]         ['dec']-= 1<<16
   measurements['gyro_y']              = {}
   measurements['gyro_y']             ['hex'] = binascii.hexlify(received_payload[26:28])
   measurements['gyro_y']             ['dec'] = int(measurements['gyro_y']['hex'],16)
   if (measurements['gyro_y']['dec']>>15==1):
      measurements['gyro_y' ]         ['dec']-= 1<<16
   measurements['gyro_z']              = {}
   measurements['gyro_z']             ['hex'] = binascii.hexlify(received_payload[28:30])
   measurements['gyro_z']             ['dec'] = int(measurements['gyro_z']['hex'],16)
   if (measurements['gyro_z']['dec']>>15==1):
      measurements['gyro_z' ]         ['dec']-= 1<<16
   #display measurements as text
   imu_reply  = ''
   if (imuChoices['sensitive_accel'].get()==1):
      imu_reply += "sensitive_accel    X  : 0x"
      imu_reply +=           measurements['sensitive_accel_x' ] ['hex']   + " = "
      imu_reply += str(      measurements['sensitive_accel_x' ] ['dec'])  + " = "
      imu_reply += str(round(measurements['sensitive_accel_x' ] ['v'],3)) +" V = "
      imu_reply += str(round(measurements['sensitive_accel_x' ] ['G'],3)) +" G\n"
      imu_reply += "                   Y  : 0x"
      imu_reply +=           measurements['sensitive_accel_y' ] ['hex']   + " = "
      imu_reply += str(      measurements['sensitive_accel_y' ] ['dec'])  + " = "
      imu_reply += str(round(measurements['sensitive_accel_y' ] ['v'],3)) +" V = "
      imu_reply += str(round(measurements['sensitive_accel_y' ] ['G'],3)) +" G\n"
      imu_reply += "                   Z1 : 0x"
      imu_reply +=           measurements['sensitive_accel_z1'] ['hex']   + " = "
      imu_reply += str(      measurements['sensitive_accel_z1'] ['dec'])  + " = "
      imu_reply += str(round(measurements['sensitive_accel_z1'] ['v'],3)) +" V = "
      imu_reply += str(round(measurements['sensitive_accel_z1'] ['G'],3)) +" G\n"
      imu_reply += "                   Z3 : 0x"
      imu_reply +=           measurements['sensitive_accel_z3'] ['hex']   + " = "
      imu_reply += str(      measurements['sensitive_accel_z3'] ['dec'])  + " = "
      imu_reply += str(round(measurements['sensitive_accel_z3'] ['v'],3)) +" V = "
      imu_reply += str(round(measurements['sensitive_accel_z3'] ['G'],3)) +" G\n"
      imu_reply += "\n"
   if (imuChoices['temperature'].get()==1):
      imu_reply += "temperature           : 0x"
      imu_reply +=           measurements['temperature']        ['hex']   + " = "
      imu_reply += str(      measurements['temperature']        ['dec'])  + " = "
      imu_reply += str(round(measurements['temperature']        ['v'],3)) +" V = "
      imu_reply += str(round(measurements['temperature']        ['C'],3)) +" C\n"
      imu_reply += "\n"
   if (imuChoices['magnetometer'].get()==1):
      imu_reply += "magnetometer       X  : 0x"
      imu_reply +=           measurements['magnetometer_x']['hex'] +" = "
      imu_reply += str(      measurements['magnetometer_x']['dec'])+" = "
      imu_reply += str(round(measurements['magnetometer_x']['Ga' ],3))+" Ga\n"
      imu_reply += "                   Y  : 0x"
      imu_reply +=           measurements['magnetometer_y']['hex'] +" = "
      imu_reply += str(      measurements['magnetometer_y']['dec'])+" = "
      imu_reply += str(round(measurements['magnetometer_y']['Ga' ],3))+" Ga\n"
      imu_reply += "                   Z  : 0x"
      imu_reply +=           measurements['magnetometer_z']['hex'] +" = "
      imu_reply += str(      measurements['magnetometer_z']['dec'])+" = "
      imu_reply += str(round(measurements['magnetometer_z']['Ga' ],3))+" Ga\n"
      imu_reply += "\n"
   if (imuChoices['large_range_accel'].get()==1):
      imu_reply += "large_range_accel  X  : 0x"
      imu_reply +=           measurements['large_range_accel_x']['hex']   + " = "
      imu_reply += str(      measurements['large_range_accel_x']['dec'])  + " = "
      imu_reply += str(round(measurements['large_range_accel_x']['G'],3)) +" G\n"
      imu_reply += "                   Y  : 0x"
      imu_reply +=           measurements['large_range_accel_y']['hex']   + " = "
      imu_reply += str(      measurements['large_range_accel_y']['dec'])  + " = "
      imu_reply += str(round(measurements['large_range_accel_y']['G'],3)) +" G\n"
      imu_reply += "                   Z  : 0x"
      imu_reply +=           measurements['large_range_accel_z']['hex']   + " = "
      imu_reply += str(      measurements['large_range_accel_z']['dec'])  + " = "
      imu_reply += str(round(measurements['large_range_accel_z']['G'],3)) +" G\n"
      imu_reply += "\n"
   if (imuChoices['gyro'].get()==1):
      imu_reply += "gyro_temperature      : 0x"
      imu_reply +=     measurements['gyro_temperature']   ['hex'] +" (unknown units)\n"
      imu_reply += "gyro               X  : 0x"
      imu_reply +=     measurements['gyro_x']             ['hex'] +" = "
      imu_reply += str(measurements['gyro_x']             ['dec'])+" o/s\n"
      imu_reply += "                   Y  : 0x"
      imu_reply +=     measurements['gyro_y']             ['hex'] +" = "
      imu_reply += str(measurements['gyro_y']             ['dec'])+" o/s\n"
      imu_reply += "                   Z  : 0x"
      imu_reply +=     measurements['gyro_z']             ['hex'] +" = "
      imu_reply += str(measurements['gyro_z']             ['dec'])+" o/s"
      imu_reply += "\n"
   guiLock.acquire()
   imuReplyLabel.config(text=imu_reply)
   guiLock.release()
   #display measurements graphically
   temp_width = 0
   imuCanvas.delete(Tkinter.ALL)
   if (imuChoices['sensitive_accel'].get()==1):
      imuSensitiveAccelImage  = imuCanvas.create_image(temp_width,0,image=imuSensitiveAccelPhoto,anchor=Tkinter.NW)
      temp_width += 200
   if (imuChoices['magnetometer'].get()==1):
      imuMagnetometerImage    = imuCanvas.create_image(temp_width,0,image=imuMagnetometerPhoto,anchor=Tkinter.NW)
      temp_width += 200
   if (imuChoices['large_range_accel'].get()==1):
      imuLargeRangeAccelImage = imuCanvas.create_image(temp_width,0,image=imuLargeRangeAccelPhoto,anchor=Tkinter.NW)
      temp_width += 200
   if (imuChoices['gyro'].get()==1):
      imuGyroImage            = imuCanvas.create_image(temp_width,0,image=imuGyroPhoto,anchor=Tkinter.NW)
      temp_width += 200
   guiLock.acquire()
   imuCanvas.config(width=temp_width,height=150)
   guiLock.release()

#==================== imuFrame

imuFrame = Tkinter.Frame(rightFrame)

imuCanvas=Tkinter.Canvas(imuFrame,width=0,height=0)
try:
   imuSensitiveAccelPhoto  = Tkinter.PhotoImage(file="../../docs/multimedia/orientation_sensitive_xl.gif")
   imuMagnetometerPhoto    = Tkinter.PhotoImage(file="../../docs/multimedia/orientation_mag.gif")
   imuLargeRangeAccelPhoto = Tkinter.PhotoImage(file="../../docs/multimedia/orientation_large-range_xl.gif")
   imuGyroPhoto            = Tkinter.PhotoImage(file="../../docs/multimedia/orientation_gyro.gif")
except:
   imuSensitiveAccelPhoto  = Tkinter.PhotoImage()
   imuMagnetometerPhoto    = Tkinter.PhotoImage()
   imuLargeRangeAccelPhoto = Tkinter.PhotoImage()
   imuGyroPhoto            = Tkinter.PhotoImage()
imuCanvas.grid(row=0,column=0,columnspan=2)

imuChoicesFrame = Tkinter.Frame(imuFrame,borderwidth=1,relief=Tkinter.RAISED)
imuChoices = {}
imuChoices['sensitive_accel']   = Tkinter.IntVar()
imuChoices['sensitive_accel'].set(1)
temp = Tkinter.Checkbutton(imuChoicesFrame, text="sensitive accelerometer"  , var=imuChoices['sensitive_accel'])
temp.grid(row=0,column=0,columnspan=2,sticky=Tkinter.W)
imuChoices['temperature']       = Tkinter.IntVar()
temp = Tkinter.Checkbutton(imuChoicesFrame, text="temperature sensor"       , var=imuChoices['temperature'])
temp.grid(row=1,column=0,columnspan=2,sticky=Tkinter.W)
imuChoices['magnetometer']      = Tkinter.IntVar()
temp = Tkinter.Checkbutton(imuChoicesFrame, text="magnetometer"             , var=imuChoices['magnetometer'])
temp.grid(row=2,column=0,columnspan=2,sticky=Tkinter.W)
imuChoices['large_range_accel'] = Tkinter.IntVar()
temp = Tkinter.Checkbutton(imuChoicesFrame, text="large-range accelerometer", var=imuChoices['large_range_accel'])
temp.grid(row=3,column=0,columnspan=2,sticky=Tkinter.W)
imuChoices['gyro']              = Tkinter.IntVar()
temp = Tkinter.Checkbutton(imuChoicesFrame, text="gyroscope"                , var=imuChoices['gyro'])
temp.grid(row=4,column=0,columnspan=2,sticky=Tkinter.W)
temp = Tkinter.Label(imuChoicesFrame, text="number measurements")
#temp.grid(row=5,column=0)
imuChoices['num_measurements'] = Tkinter.Text(imuChoicesFrame,width=4,height=1)
imuChoices['num_measurements'].insert(Tkinter.END,'1')
#imuChoices['num_measurements'].grid(row=5,column=1)
temp = Tkinter.Button(imuChoicesFrame, text="Go", command=imu_send)
temp.grid(row=6,column=0,columnspan=2)
imuChoicesFrame.grid(row=1,column=0)

imuReplyLabel = Tkinter.Label(imuFrame,text='',font=("Courier", 10),justify=Tkinter.LEFT)
imuReplyLabel.grid(row=1,column=1)

#-------------------- udpLed functions

def udpLed_send():
   ledChar = 0
   if (ledChoices[0].get()==1):
      ledChar += 1<<3
   if (ledChoices[1].get()==1):
      ledChar += 1<<2
   if (ledChoices[2].get()==1):
      ledChar += 1<<1
   if (ledChoices[3].get()==1):
      ledChar += 1<<0
   udp_proxy_send(str(chr(ledChar)),WKP_SCRIPT_UDP_LED,WKP_GINA_UDP_LED)

#==================== udpLedFrame

udpLedFrame = Tkinter.Frame(rightFrame)

ledChoices = {}
ledChoices[0] = Tkinter.IntVar()
temp = Tkinter.Checkbutton(udpLedFrame, text=""  , var=ledChoices[0])
temp.config(background='red')
temp.grid(row=0,column=0)
ledChoices[1] = Tkinter.IntVar()
temp = Tkinter.Checkbutton(udpLedFrame, text=""  , var=ledChoices[1])
temp.config(background='blue')
temp.grid(row=0,column=1)
ledChoices[2] = Tkinter.IntVar()
temp = Tkinter.Checkbutton(udpLedFrame, text=""  , var=ledChoices[2])
temp.config(background='green')
temp.grid(row=0,column=2)
ledChoices[3] = Tkinter.IntVar()
temp = Tkinter.Checkbutton(udpLedFrame, text=""  , var=ledChoices[3])
temp.config(background='red')
temp.grid(row=0,column=3)
udpLedButton = Tkinter.Button(udpLedFrame, text="Set Leds", command=udpLed_send)
udpLedButton.grid(row=1,column=0,columnspan=4)

#-------------------- udpEcho functions

def udpEcho_send():
   global udpEcho_timestamp, guiLock
   udpEcho_timestamp = time.time()
   udp_proxy_send('abcdef',WKP_SCRIPT_UDP_ECHO,WKP_GINA_UDP_ECHO)
   guiLock.acquire()
   udpEchoText.config(text="waiting for reply...")
   guiLock.release()

def udpEcho_receive(received_payload):
   global guiLock
   if (received_payload=='abcdef'):
      guiLock.acquire()
      udpEchoText.config(text="reply after "+str(round((time.time()-udpEcho_timestamp)*1000))+"ms")
      guiLock.release()
   else:
      print "Error udpEcho_receive: wrong payload"

#==================== udpEchoFrame

udpEchoFrame = Tkinter.Frame(rightFrame)

udpEchoButton = Tkinter.Button(udpEchoFrame, text="udpEcho", command=udpEcho_send)
udpEchoButton.grid(row=0,column=0)

udpEchoText   = Tkinter.Label(udpEchoFrame,text="")
udpEchoText.grid(row=0,column=1)

udpEcho_timestamp = 0

#-------------------- heli functions

MOTOR_MAX        = 100.0
MOTOR_MIN        =   0.0
MOTOR_STEP       =   5.0

motor1_command = 0
motor2_command = 0

def heli_up():
   global motor1_command, motor2_command
   if (motor1_command+MOTOR_STEP<=MOTOR_MAX and motor2_command+MOTOR_STEP<=MOTOR_MAX):
      motor1_command += MOTOR_STEP
      motor2_command += MOTOR_STEP
      heli_send_command()

def heli_down():
   global motor1_command, motor2_command
   if (motor1_command-MOTOR_STEP>=MOTOR_MIN and motor2_command-MOTOR_STEP>=MOTOR_MIN):
      motor1_command -= MOTOR_STEP
      motor2_command -= MOTOR_STEP
      heli_send_command()

def heli_left():
   global motor1_command
   if (motor1_command+MOTOR_STEP<=MOTOR_MAX):
      motor1_command += MOTOR_STEP
      heli_send_command()

def heli_right():
   global motor1_command
   if (motor1_command-MOTOR_STEP>=MOTOR_MIN):
      motor1_command -= MOTOR_STEP
      heli_send_command()

def heli_stop():
   global motor1_command, motor2_command
   motor1_command = 0
   motor2_command = 0
   heli_send_command()

def heli_takeoff():
   global motor1_command, motor2_command
   motor1_command = 0x004d
   motor2_command = 0x004d
   heli_send_command()

def heli_land():
   global motor1_command, motor2_command
   motor1_command = 0x003e
   motor2_command = 0x003e
   heli_send_command()

def heli_clicked(event):
   global motor1_command, motor2_command, heliCanvas
   heliCanvas.focus_set()
   if (event.x>100 and event.x<200 and event.y>0   and event.y<100):
      heli_up()
   if (event.x>0   and event.x<100 and event.y>100 and event.y<200):
      heli_left()
   if (event.x>200 and event.x<300 and event.y>100 and event.y<200):
      heli_right()
   if (event.x>100 and event.x<200 and event.y>200 and event.y<300):
      heli_down()
   if (event.x>100 and event.x<200 and event.y>100 and event.y<200):
      heli_stop()
   if (event.x>200 and event.x<300 and event.y>0   and event.y<100):
      heli_takeoff()
   if (event.x>200 and event.x<300 and event.y>200 and event.y<300):
      heli_land()
   if (event.y>310 and event.y<340):
      motor1_command = event.x/300.0*MOTOR_MAX
      heli_send_command()
   if (event.y>340 and event.y<360):
      motor_diff = motor1_command-motor2_command
      motor1_command = (event.x/300.0*MOTOR_MAX)+(motor_diff/2.0)
      if motor1_command>MOTOR_MAX:
         motor1_command=MOTOR_MAX
      motor2_command = (event.x/300.0*MOTOR_MAX)-(motor_diff/2.0)
      if motor2_command>MOTOR_MAX:
         motor2_command=MOTOR_MAX
      heli_send_command()
   if (event.y>360 and event.y<390):
      motor2_command = event.x/300.0*MOTOR_MAX
      heli_send_command()

def heli_send_command():
   #update the sliders
   heliCanvas.delete("temp_slider")
   heliCanvas.create_rectangle(  2,310,(motor1_command/MOTOR_MAX)*300.0,340,fill="yellow",tag="temp_slider")
   heliCanvas.create_rectangle(  2,360,(motor2_command/MOTOR_MAX)*300.0,390,fill="yellow",tag="temp_slider")
   #send the command over udp_proxy
   heli_command = []
   heli_command.append(chr(int(motor1_command/256)))
   heli_command.append(chr(int(motor1_command%256)))
   heli_command.append(chr(int(motor2_command/256)))
   heli_command.append(chr(int(motor2_command%256)))
   heli_command = ''.join(heli_command)
   udp_proxy_send(heli_command,WKP_SCRIPT_UDP_HELI,WKP_GINA_UDP_HELI)

#==================== heliFrame

heliFrame = Tkinter.Frame(rightFrame)

heliCanvas=Tkinter.Canvas(heliFrame,width=300,height=400,takefocus=1)
heliCanvas.bind("<Button-1>",heli_clicked)
heliCanvas.bind("<Button-2>",heli_clicked)
heliCanvas.bind("<Button-3>",heli_clicked)
heliCanvas.create_rectangle(100,  2,200,100,fill="#00ffff")
heliCanvas.create_text(150,50,text="up <i>")
heliCanvas.create_rectangle(  2,100,100,200,fill="#00ffff")
heliCanvas.create_text(50,150,text="left <j>")
heliCanvas.create_rectangle(200,100,300,200,fill="#00ffff")
heliCanvas.create_text(250,150,text="right <l>")
heliCanvas.create_rectangle(100,200,200,300,fill="#00ffff")
heliCanvas.create_text(150,250,text="down <k>")
heliCanvas.create_oval(120,120,180,180,fill="red")
heliCanvas.create_text(150,150,text="stop!\n<space>")
heliCanvas.create_oval(220, 20,280, 80,fill="green")
heliCanvas.create_text(250, 50,text="takeoff <q>")
heliCanvas.create_oval(220,220,280,280,fill="green")
heliCanvas.create_text(250,250,text="land <a>")
heliCanvas.create_rectangle(  2,310,300,340)
heliCanvas.create_text(150,325,text="motor 1")
heliCanvas.create_rectangle(  2,360,300,390)
heliCanvas.create_text(150,375,text="motor 2")
heliCanvas.grid(row=0,column=0)

rightFrame.grid(row=0,column=1)

#-------------------- warpwing functions

def warpwing_start():
   warpwing_period = warpwingPeriodInput.get(1.0,Tkinter.END)
   warpwing_channel = warpwingChannelInput.get(1.0,Tkinter.END)
      
   warpwing_command = []
   warpwing_command.append(chr(int(warpwing_channel)))
   warpwing_command.append(chr(int(warpwing_period) / 256))
   warpwing_command.append(chr(int(warpwing_period) % 256))

   warpwing_command_str = ''.join(warpwing_command)
   udp_proxy_send(warpwing_command_str,WKP_SCRIPT_UDP_WARPWING,WKP_GINA_UDP_WARPWING)

def warpwing_stop():
   warpwing_period = 0
   warpwing_channel = warpwingChannelInput.get(1.0,Tkinter.END)
      
   warpwing_command = []
   warpwing_command.append(chr(int(warpwing_channel)))
   warpwing_command.append(chr(int(warpwing_period) / 256))
   warpwing_command.append(chr(int(warpwing_period) % 256))

   warpwing_command_str = ''.join(warpwing_command)
   udp_proxy_send(warpwing_command_str,WKP_SCRIPT_UDP_WARPWING,WKP_GINA_UDP_WARPWING)

#==================== warpwingFrame

warpwingFrame = Tkinter.Frame(rightFrame)

warpwingStartButton = Tkinter.Button(warpwingFrame, text="Start sending", command=warpwing_start)
warpwingStartButton.grid(row=0,column=0,columnspan=2)

temp = Tkinter.Label(warpwingFrame, text="Period:")
temp.grid(row=1,column=0)

warpwingPeriodInput = Tkinter.Text(warpwingFrame,width=5,height=1)
warpwingPeriodInput.insert(Tkinter.END,"1024")
warpwingPeriodInput.grid(row=1,column=1)

temp = Tkinter.Label(warpwingFrame, text="Channel:")
temp.grid(row=2,column=0)

warpwingChannelInput = Tkinter.Text(warpwingFrame,width=5,height=1)
warpwingChannelInput.insert(Tkinter.END,"20")
warpwingChannelInput.grid(row=2,column=1)

temp = Tkinter.Label(warpwingFrame, text="")
temp.grid(row=3,column=0)

warpwingStopButton = Tkinter.Button(warpwingFrame, text="Stop sending", command=warpwing_stop)
warpwingStopButton.grid(row=4,column=0,columnspan=2)

#================================= udp_proxy ============================================

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

def udp_proxy_send(udp_payload_to_send,udp_source_port,udp_destination_port):
   global dataToSend, dataToSendLock, guiLock
   global connectionType
   if (connectionType.get()=="IPv6"):
      print "\n========================= to IPv6 ===================================="
      print "\n--UDP datagram--"
      print "source port : "     +str(udp_source_port)     +"="+hex(udp_source_port)
      print "destination port: " +str(udp_destination_port)+"="+hex(udp_destination_port)
      print "payload: "          +binascii.hexlify(udp_payload_to_send)
      guiLock.acquire()
      hisAddress = connectionAddress.get(1.0,Tkinter.END)
      guiLock.release()
      hisAddress = hisAddress[0:len(hisAddress)-1]
      try:
         socketThreadHandlerv6[udp_source_port].sendto(udp_payload_to_send,hisAddress,udp_destination_port)
      except:
         err = sys.exc_info()
         sys.stderr.write( "Error: %s (%s) \n" % (str(err[0]), str(err[1])))
         guiLock.acquire()
         connectionAddress.config(background="red")
         guiLock.release()
         if (ipv6supported==False):
            print "WARNING: IPv6 not enabled on your computer"
      else:
         guiLock.acquire()
         connectionAddress.config(background="green")
         guiLock.release()
   if (connectionType.get()=="IPv4"):
      print "\n========================= to IPv4 ===================================="
      hisAddress = get_full_connectionAddress()
      guiLock.acquire()
      proxyServerAddress = proxyAddress.get(1.0,Tkinter.END)
      guiLock.release()
      proxyServerAddress = proxyServerAddress[0:len(proxyServerAddress)-1]
      if (hisAddress!=''):
         print "\nproxy's IPv4 address: " + proxyServerAddress
         print "\n--proxy packet--"
         proxyPayload  = ''
         print "mote's IPv6 address: "  + hisAddress
         proxyPayload += hisAddress                 #32 bytes
         print "destination port: "     + str(udp_destination_port)+"="+hex(udp_destination_port)
         string_udp_destination_port = str(udp_destination_port)
         while (len(string_udp_destination_port)<4):
            string_udp_destination_port = '0'+string_udp_destination_port
         proxyPayload += string_udp_destination_port #4 bytes
         print "payload: "              + binascii.hexlify(udp_payload_to_send)
         proxyPayload += udp_payload_to_send
         try:
            socketThreadHandlerv4[udp_source_port].sendto(proxyPayload,proxyServerAddress,WKP_PROXY_SERVER)
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error: %s (%s) \n" % (str(err[0]), str(err[1])))
            guiLock.acquire()
            proxyAddress.config(background="red")
            guiLock.release()
            if (ipv6supported==False):
               print "WARNING: IPv6 not enabled on your computer"
         else:
            guiLock.acquire()
            proxyAddress.config(background="green")
            guiLock.release()
   elif (connectionType.get()=="basestation"):
      print "\n========================= to basestation ================================="
      #put udp payload in UDP header
      udp_datagram  = ''
      udp_datagram += chr(udp_source_port/256)             #source port
      udp_datagram += chr(udp_source_port%256)
      udp_datagram += chr(udp_destination_port/256)        #destination port
      udp_datagram += chr(udp_destination_port%256)
      udp_datagram += chr((8+len(udp_payload_to_send))/256)#length
      udp_datagram += chr((8+len(udp_payload_to_send))%256)
      udp_datagram += chr(0)                               #checksum
      udp_datagram += chr(0)
      udp_datagram += udp_payload_to_send
      #put udp packet in IPv6 header
      ipv6_pkt_disassambled = {};
      ipv6_pkt_disassambled['version']        = 6
      ipv6_pkt_disassambled['traffic_class']  = 0
      ipv6_pkt_disassambled['flow_label']     = 0
      ipv6_pkt_disassambled['payload_length'] = len(udp_datagram)
      ipv6_pkt_disassambled['next_header']    = 0x11
      ipv6_pkt_disassambled['hop_limit']      = 1
      ipv6_pkt_disassambled['src_addr']       = ''
      for i in range(0,16):
        ipv6_pkt_disassambled['src_addr'] += chr(0) #don't put address, will be elided anyway
      ipv6_pkt_disassambled['dst_addr']       = ''
      for i in range(0,16):
        ipv6_pkt_disassambled['dst_addr'] += chr(0) #don't put address, will be elided anyway
      ipv6_pkt_disassambled['payload']        = udp_datagram
      print_ipv6(ipv6_pkt_disassambled)
      #compress IPv6 packet using 6LoWPAN
      lowpan_pkt = ipv6_to_lowpan(ipv6_pkt_disassambled, IPHC_TF_ELIDED, IPHC_NH_INLINE, IPHC_HLIM_INLINE, \
                                  IPHC_CID_NO, IPHC_SAC_STATELESS, IPHC_SAM_ELIDED, IPHC_M_NO, \
                                  IPHC_DAC_STATELESS, IPHC_DAM_ELIDED)
      print_lowpan(lowpan_pkt)
      #retrieve next hop and send
      nextHop_string = get_full_connectionAddress()
      if (len(nextHop_string)==32):
         guiLock.acquire()
         connectionAddress.config(background="green")
         guiLock.release()
         nextHop_string = nextHop_string[16:]
         nextHop = ''
         for i in range(0,8):
            nextHop += chr(int(nextHop_string[2*i:2*i+2],16))
         dataToSendLock.acquire()
         dataToSend = nextHop + lowpan_pkt
         guiLock.acquire()
         connectionCanvas.itemconfig(connectionCanvas.find_withtag("pending_data_led")[0],fill="yellow")
         guiLock.release()
         dataToSendLock.release()
      else:
         guiLock.acquire()
         connectionAddress.config(background="red")
         guiLock.release()
         if (ipv6supported==False):
            print "WARNING: IPv6 not enabled on your computer"

def udp_proxy_receive(src_address,udp_dest_port,udp_paylad):
   print "\n--UDP datagram--"
   if (src_address=='00000000000000000000000000000000'):
      print "source address: (elided)"
   else:
      print "source address: "+src_address
   print "destination port: "+str(udp_dest_port)+"="+hex(udp_dest_port)
   print "payload: 0x"+binascii.hexlify(udp_paylad)
   if (udp_dest_port==WKP_SCRIPT_UDP_GINA):
      imu_receive(udp_paylad)
   elif (udp_dest_port==WKP_SCRIPT_UDP_ECHO):
      udpEcho_receive(udp_paylad)
   else:
      print "Error udp_proxy_receive unsupported dst_port=="+str(udp_dest_port)

def get_full_connectionAddress():
   global guiLock
   guiLock.acquire()
   temp_connectionAddress = connectionAddress.get(1.0,Tkinter.END)
   guiLock.release()
   temp_connectionAddress = temp_connectionAddress[:len(temp_connectionAddress)-1]     #remove trailing character
   #disassemble IPv6 address in address_units
   address_blocks = temp_connectionAddress.split('::')
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

# print 6lowPAN packet
def print_lowpan(pkt6):
   print "\n--6LowPAN packet--"
   output_wireshark(pkt6)

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
      pkt_ipv6['src_addr'] = ''
      for i in range(0,16):
        pkt_ipv6['src_addr'] += chr(0)
   elif (sam == IPHC_SAM_16B):
      a1 = pkt_lowpan[ptr]
      a2 = pkt_lowpan[ptr+1]
      ptr = ptr+2
      s = ''.join(['\x00','\x00','\x00','\x00','\x00','\x00',a1,a2])
      pkt_ipv6['src_addr'] = IP64B_PREFIX+s
   elif (sam == IPHC_SAM_64B):
      pkt_ipv6['src_addr'] = IP64B_PREFIX+join(pkt_lowpan[ptr:ptr+8])
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
      pkt_ipv6['dst_addr'] = ''
      for i in range(0,16):
        pkt_ipv6['dst_addr'] += chr(0)
   elif (dam == IPHC_DAM_16B):
      a1 = pkt_lowpan[ptr]
      a2 = pkt_lowpan[ptr+1]
      ptr = ptr+2
      s = ''.join(['\x00','\x00','\x00','\x00','\x00','\x00',a1,a2])
      pkt_ipv6['dst_addr'] = IP64B_PREFIX+s
   elif (dam == IPHC_DAM_64B):
      pkt_ipv6['dst_addr'] = IP64B_PREFIX+join(pkt_lowpan[ptr:ptr+8])
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

# print IPv6 packet (input: disassembled IPv6 packet)
def print_ipv6(pkt):
   print "\n--IPv6 packet--"
   print "Version: "       + str(pkt['version'])
   print "Traffic class: " + str(pkt['traffic_class'])
   print "Flow label: "    + str(pkt['flow_label'])
   print "Payload length: "+ str(pkt['payload_length']) +"="+hex(int(pkt['payload_length']))
   print "Next header: "   + str(pkt['next_header']) +"="+hex(int(pkt['next_header']))
   print "Hop limit: "     + str(pkt['hop_limit'])
   if (pkt['src_addr'][15]==chr(0)):
      print "Src address: (elided)"
   else:
      print "Src address:",binascii.hexlify(pkt['src_addr'])
   if (pkt['dst_addr'][15]==chr(0)):
      print "Dst address: (elided)"
   else:
      print "Dst address: "+binascii.hexlify(pkt['dst_addr'])
   print "Payload: 0x"+binascii.hexlify(pkt['payload'])
   pkt_reassembled = reassemble_ipv6_packet(pkt)
   output_wireshark(pkt_reassembled)

#================================= moteThread ================================================

def findSerialPortsNames():
   serialport_names = []
   if ihaveamac==1:
      serialport_names.append('/dev/tty.SLAB_USBtoUART')
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

class moteThread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
   def run(self):
      global serialHandler,moteThread_active, guiLock
      print 'starting moteThread'
      while True:
         availableports = findSerialPortsNames()
         if (len(availableports)>0):
            try:
               serialHandler = serial.Serial(availableports[0],baudrate=115200,timeout=5)
            except:
               err = sys.exc_info()
               errorMessage = " ERROR [moteThread] 1: "+str(err[0])+" ("+str(err[1])+")"
               sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
               print errorMessage
            else:
               guiLock.acquire()
               connectionCanvas.itemconfig(connectionCanvas.find_withtag("basestation_connected_led")[0],fill="green")
               connectionCanvas.itemconfig(connectionCanvas.find_withtag("basestation_connected_text")[0],text=serialHandler.portstr)
               guiLock.release()
               print "moteThread connected to "+serialHandler.portstr
               dataToSendLock.acquire()
               dataToSend = ''
               dataToSendLock.release()
               state = "WAIT_HEADER"
               numdelimiter = 0
               while True:
                     if (moteThread_active==0):
                        print 'moteThread exiting.'
                        return
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
            guiLock.acquire()
            connectionCanvas.itemconfig(connectionCanvas.find_withtag("basestation_connected_led")[0],fill="red")
            connectionCanvas.itemconfig(connectionCanvas.find_withtag("basestation_connected_text")[0],text="")
            guiLock.release()
            time.sleep(1)

def parseInput(input):
   global dataToSend, dataToSendLock, commandToSend, commandToSendLock, disable_bridge, guiLock
   #byte 0 is the type of status message
   if (input[0]=="S"):
      advance_status_from_basestation_led()
   elif (input[0]=="E"):
      advance_error_from_basestation_led()
   elif (input[0]=="D"):
      advance_data_from_basestation_led()
      #input[0] is "D", input[1:2] is the addr_16b
      pkt_lowpan = input[3:]
      pkt_ipv6_disassembled = lowpan_to_ipv6(pkt_lowpan)
      #pkt_ipv6 = reassemble_ipv6_packet(pkt_ipv6_disassembled)
      if (pkt_ipv6_disassembled['next_header']==0x11):
         print "\n========================= from basestation ==============================="
         print_lowpan(pkt_lowpan)
         print_ipv6(pkt_ipv6_disassembled)
         udp_data_disassembled = {}
         udp_data_disassembled['src_port'] = ord(pkt_ipv6_disassembled['payload'][0])*256+ord(pkt_ipv6_disassembled['payload'][1])
         udp_data_disassembled['dst_port'] = ord(pkt_ipv6_disassembled['payload'][2])*256+ord(pkt_ipv6_disassembled['payload'][3])
         udp_data_disassembled['length']   = ord(pkt_ipv6_disassembled['payload'][4])*256+ord(pkt_ipv6_disassembled['payload'][5])
         udp_data_disassembled['cheksum']  = ord(pkt_ipv6_disassembled['payload'][6])*256+ord(pkt_ipv6_disassembled['payload'][7])
         udp_data_disassembled['payload']  = pkt_ipv6_disassembled['payload'][8:]
         udp_proxy_receive(binascii.hexlify(pkt_ipv6_disassembled['src_addr']),udp_data_disassembled['dst_port'],udp_data_disassembled['payload'])
   elif (input[0]=="R"):   #waiting for command
      advance_request_from_basestation_led()
      if (ord(input[1])==200):  #input buffer empty
         dataToSendLock.acquire()
         commandToSendLock.acquire()
         if (len(dataToSend)>0):
            serialHandler.write('D')
            serialHandler.write(chr(len(dataToSend)))
            serialHandler.write(dataToSend)
            dataToSend = ''
            guiLock.acquire()
            connectionCanvas.itemconfig(connectionCanvas.find_withtag("pending_data_led")[0],fill="")
            guiLock.release()
         elif (len(commandToSend)>0):
            serialHandler.write(commandToSend)
            commandToSend = ''
            guiLock.acquire()
            connectionCanvas.itemconfig(connectionCanvas.find_withtag("pending_command_led")[0],fill="")
            guiLock.release()
         else:
            if (disable_bridge==1):
               print 'stopping bridge mode...'
               serialHandler.write('B')
               serialHandler.write(chr(1+len(IP64B_PREFIX)))
               serialHandler.write('N')
               serialHandler.write(IP64B_PREFIX)
            else:
               serialHandler.write('B')
               serialHandler.write(chr(1+len(IP64B_PREFIX)))
               serialHandler.write('Y')
               serialHandler.write(IP64B_PREFIX)
         commandToSendLock.release()
         dataToSendLock.release()

def advance_status_from_basestation_led():
   global guiLock
   if (connectionCanvas.itemcget(connectionCanvas.find_withtag("status_from_basestation_led")[0],"fill")==""):
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("status_from_basestation_led")[0],fill="green")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("status_from_basestation_led")[1],fill="")
      guiLock.release()
   else:
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("status_from_basestation_led")[0],fill="")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("status_from_basestation_led")[1],fill="green")
      guiLock.release()

def advance_error_from_basestation_led():
   global guiLock
   if (connectionCanvas.itemcget(connectionCanvas.find_withtag("error_from_basestation_led")[0],"fill")==""):
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("error_from_basestation_led")[0],fill="green")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("error_from_basestation_led")[1],fill="")
      guiLock.release()
   else:
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("error_from_basestation_led")[0],fill="")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("error_from_basestation_led")[1],fill="green")
      guiLock.release()

def advance_data_from_basestation_led():
   global guiLock
   if (connectionCanvas.itemcget(connectionCanvas.find_withtag("data_from_basestation_led")[0],"fill")==""):
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("data_from_basestation_led")[0],fill="green")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("data_from_basestation_led")[1],fill="")
      guiLock.release()
   else:
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("data_from_basestation_led")[0],fill="")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("data_from_basestation_led")[1],fill="green")
      guiLock.release()

def advance_request_from_basestation_led():
   global guiLock
   if (connectionCanvas.itemcget(connectionCanvas.find_withtag("request_from_basestation_led")[0],"fill")==""):
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("request_from_basestation_led")[0],fill="green")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("request_from_basestation_led")[1],fill="")
      guiLock.release()
   else:
      guiLock.acquire()
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("request_from_basestation_led")[0],fill="")
      connectionCanvas.itemconfig(connectionCanvas.find_withtag("request_from_basestation_led")[1],fill="green")
      guiLock.release()

#============================ socketThread ==============================================

class socketThread(threading.Thread):
   def __init__(self,myPort,type):
      self.myPort = myPort
      print "starting socketThread on port "+str(self.myPort)
      if (type=='IPv4'):
         self.socket_handler = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      else:
         self.socket_handler = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
      self.socket_handler.bind((myAddress,myPort))
      threading.Thread.__init__(self)
   def run(self):
      global serialOutput, socketThreads_active
      while True:
         if (socketThreads_active==0):
            print "socketThread on port "+str(self.myPort)+" exiting."
            return #poipoi learn how a function can kill a thread
         try:
            networkInput,dist_addr = self.socket_handler.recvfrom(1024)
            print "\n========================= from IPv6 =================================="
            udp_proxy_receive(dist_addr[0],self.myPort,networkInput)
         except socket.error:
            err = sys.exc_info()
            errorMessage = " ERROR [socketThread]: could not receive ("+str(err[0])+" "+str(err[1])+")"
            sys.stderr.write("\n"+datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+errorMessage)
            print errorMessage
            break
   def sendto(self,udp_payload_to_send,hisAddress,udp_destination_port):
      try:
         self.socket_handler.sendto(udp_payload_to_send,(hisAddress,udp_destination_port))
      except socket.error:
         return 0
      else:
         return 1

#================================= main =============================

socketThreads_active=1
moteThread_active=1
disable_bridge=0

#declare threads
moteThreadHandler                        = moteThread()
socketThreadHandlerv6                    = {}
try:
   socketThreadHandlerv6[WKP_SCRIPT_UDP_ECHO] = socketThread(WKP_SCRIPT_UDP_ECHO, 'IPv6')
   socketThreadHandlerv6[WKP_SCRIPT_UDP_LED ] = socketThread(WKP_SCRIPT_UDP_LED,  'IPv6')
   socketThreadHandlerv6[WKP_SCRIPT_UDP_GINA] = socketThread(WKP_SCRIPT_UDP_GINA, 'IPv6')
   socketThreadHandlerv6[WKP_SCRIPT_UDP_HELI] = socketThread(WKP_SCRIPT_UDP_HELI, 'IPv6')
except socket.error:
   print "WARNING: IPv6 not enabled on your computer"
   ipv6supported = False
else:
   ipv6supported = True
socketThreadHandlerv4                    = {}
try:
   socketThreadHandlerv4[WKP_SCRIPT_UDP_ECHO] = socketThread(WKP_SCRIPT_UDP_ECHO, 'IPv4')
   socketThreadHandlerv4[WKP_SCRIPT_UDP_LED ] = socketThread(WKP_SCRIPT_UDP_LED,  'IPv4')
   socketThreadHandlerv4[WKP_SCRIPT_UDP_GINA] = socketThread(WKP_SCRIPT_UDP_GINA, 'IPv4')
   socketThreadHandlerv4[WKP_SCRIPT_UDP_HELI] = socketThread(WKP_SCRIPT_UDP_HELI, 'IPv4')
except socket.error:
   print "WARNING: can not open IPv4 sockets"

#start threads
if ipv6supported==True:
   for key,value in socketThreadHandlerv6.items():
      value.start()
for key,value in socketThreadHandlerv4.items():
   value.start()
moteThreadHandler.start()

root.mainloop()
