#!/usr/bin/python

import time, sys, os
import binascii
import threading
import Tkinter
import lib.motetalk as motetalk
from lib.motetalk import cmd
if os.name=='nt':
   import _winreg as winreg
from visual import *

#====================================== variables =======================================

gina2header = "sens_x sens_y sens_z1 sens_z3 sens_temp mag_x mag_y mag_z"
gina2fmtstr = '     H      H       H       H         H     H     H     H'

header_line  = ''
header_line +=     'timestamp'
header_line += ' '+'sensitive_accel_x'
header_line += ' '+'sensitive_accel_y'
header_line += ' '+'sensitive_accel_z1'
header_line += ' '+'sensitive_accel_z3'
header_line += ' '+'temperature'
header_line += ' '+'magnetometer_x'
header_line += ' '+'magnetometer_y'
header_line += ' '+'magnetometer_z'
header_line += ' '+'large_range_accel_x'
header_line += ' '+'large_range_accel_y'
header_line += ' '+'large_range_accel_z'
header_line += ' '+'gyro_temperature'
header_line += ' '+'gyro_x'
header_line += ' '+'gyro_y'
header_line += ' '+'gyro_z'

guiLock      = threading.Lock()

#====================================== helper functions ================================

def findSerialPortsNames():
   serialport_names = []
   if (os.name=='nt' or os.name=='posix'):
      path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
      key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
      for i in range(winreg.QueryInfoKey(key)[1]):
         try:
            val = winreg.EnumValue(key,i)
         except:
            pass
         else:
            if (val[0].find('USBSER')>-1):
               serialport_names.append(str(val[1]))
   elif os.name=='posix':
      serialport_names = glob.glob('/dev/ttyUSB*')
   serialport_names.sort()
   return serialport_names

def crc(bytes):
  c = 0
  for b in bytes:
    c = c ^ ord(b)
    for y in range(8):
      if c & 0x1:
        c = c >> 1 ^ 0x8408
      else:
        c = c >> 1
  return c

def advance_leds(ledType,serialPortName):
   return #poipoi
   global guiLock
   if (ledType=='ok'):
      color='green'
   elif (ledType=='error_crc'):
      color='yellow'
   else:
      color='red'
   if (connectionCanvas.itemcget(connectionCanvas.find_withtag("led_"+ledType+"_"+serialPortName)[0],"fill")==""):
      if (guiLock.acquire(False)==True):
         connectionCanvas.itemconfig(connectionCanvas.find_withtag("led_"+ledType+"_"+serialPortName)[0],fill=color)
         connectionCanvas.itemconfig(connectionCanvas.find_withtag("led_"+ledType+"_"+serialPortName)[1],fill="")
         guiLock.release()
   else:
      if (guiLock.acquire(False)==True):
         connectionCanvas.itemconfig(connectionCanvas.find_withtag("led_"+ledType+"_"+serialPortName)[0],fill="")
         connectionCanvas.itemconfig(connectionCanvas.find_withtag("led_"+ledType+"_"+serialPortName)[1],fill=color)
         guiLock.release()

class LockEnabledButton(Tkinter.Button):
   def tkButtonDown(self, *args):
      print 'poipoi tkButtonDown'
      guiLock.acquire()
      Tkinter.Button.tkButtonDown(self, *args)
      guiLock.release()
   def tkButtonUp(self, *args):
      print 'poipoi tkButtonUp'
      guiLock.acquire()
      Tkinter.Button.tkButtonUp(self, *args)
      guiLock.release()

#====================================== moteThread ======================================

class moteThread(threading.Thread):
   def __init__(self, serialPortName, channel):
      threading.Thread.__init__(self)
      self.serialPortName = serialPortName
      self.channel = channel
      self.done = 0
   def run(self):
      file = open("channel_"+str(self.channel)+".sensor", 'w')
      m = motetalk.motetalk(gina2fmtstr, gina2header, self.serialPortName)
      m.sendbase(cmd.radio(self.channel))
      m.sendbase(cmd.flags(cmd.ledmode_cnt + cmd.notick))
      m.sendbase(cmd.mode(cmd.mode_sniff))
      sys.stderr.write( "Sniffing from "+self.serialPortName+" on channel "+str(self.channel)+"...\n")
      file.write(header_line)
      #visual elements
      sensitive_accel_vector   = arrow(pos=(0,0,0), axis=(0,0,0), shaftwidth=0.5, color=color.green)
      magnetometer_vector      = arrow(pos=(0,0,0), axis=(0,0,0), shaftwidth=0.5, color=color.red)
      large_range_accel_vector = arrow(pos=(0,0,0), axis=(0,0,0), shaftwidth=0.5, color=color.blue)
      gyro_vector              = arrow(pos=(0,0,0), axis=(0,0,0), shaftwidth=0.5, color=color.yellow)
      #admin
      num_packets_ok           = 0
      num_packets_crc_error    = 0
      num_packets_length_error = 0
      while not self.done:
        try:
          received_payload, timestamp = m.nextline(False)
          if (received_payload == False):
            self.done = 1
            sys.stderr.write("\n** Error **")
            sys.stderr.write(repr(t) + "\n\n")
          elif received_payload:
            received_payload = received_payload.rstrip('***')
            if (crc(received_payload[:-2])!=0):
               num_packets_crc_error += 1
               advance_leds('error_crc',self.serialPortName)
            elif (len(received_payload)==34):
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
               measurements['gyro_temperature']   ['dec'] = int(measurements['gyro_temperature']['hex'],16)
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
               measurements['unknown1']            = {}
               measurements['unknown1']           ['hex'] = binascii.hexlify(received_payload[30:32])
               measurements['unknown1']           ['dec'] = int(measurements['unknown1']['hex'],16)
               measurements['unknown2']            = {}
               measurements['unknown2']           ['hex'] = binascii.hexlify(received_payload[30:32])
               measurements['unknown2']           ['dec'] = int(measurements['unknown2']['hex'],16)
               #output to file
               output  = '\n'
               output +=     str(timestamp)
               output += ' '+str(measurements['sensitive_accel_x' ]['G'])
               output += ' '+str(measurements['sensitive_accel_y' ]['G'])
               output += ' '+str(measurements['sensitive_accel_z1']['G'])
               output += ' '+str(measurements['sensitive_accel_z3']['G'])
               output += ' '+str(measurements['temperature']['C'])
               output += ' '+str(measurements['magnetometer_x']['Ga'])
               output += ' '+str(measurements['magnetometer_y']['Ga'])
               output += ' '+str(measurements['magnetometer_z']['Ga'])
               output += ' '+str(measurements['large_range_accel_x']['G'])
               output += ' '+str(measurements['large_range_accel_y']['G'])
               output += ' '+str(measurements['large_range_accel_z']['G'])
               output += ' '+str(measurements['gyro_temperature']['dec'])
               output += ' '+str(measurements['gyro_x']['dec'])
               output += ' '+str(measurements['gyro_y']['dec'])
               output += ' '+str(measurements['gyro_z']['dec'])
               file.write(output)
               #display in 3D
               sensitive_accel_magnitude   = float(sqrt(measurements['sensitive_accel_x' ]['G']**2+
                                                        measurements['sensitive_accel_y' ]['G']**2+
                                                        measurements['sensitive_accel_z1']['G']**2))
               sensitive_accel_vector.axis   = (  measurements['sensitive_accel_y' ]['G']/sensitive_accel_magnitude,
                                                  measurements['sensitive_accel_x' ]['G']/sensitive_accel_magnitude,
                                                  measurements['sensitive_accel_z1']['G']/sensitive_accel_magnitude)
               magnetometer_magnitude      = float(sqrt(measurements['magnetometer_x']['Ga']**2+
                                                        measurements['magnetometer_y']['Ga']**2+
                                                        measurements['magnetometer_z']['Ga']**2))
               magnetometer_vector.axis      = ( -measurements['magnetometer_y']['Ga']/magnetometer_magnitude,
                                                  measurements['magnetometer_x']['Ga']/magnetometer_magnitude,
                                                  measurements['magnetometer_z']['Ga']/magnetometer_magnitude)
               large_range_accel_magnitude = float(sqrt(measurements['large_range_accel_x']['G']**2+
                                                        measurements['large_range_accel_y']['G']**2+
                                                        measurements['large_range_accel_z']['G']**2))
               large_range_accel_vector.axis = ( -measurements['large_range_accel_x']['G']/large_range_accel_magnitude,
                                                 -measurements['large_range_accel_y']['G']/large_range_accel_magnitude,
                                                 -measurements['large_range_accel_z']['G']/large_range_accel_magnitude)
               gyro_magnitude              = float(sqrt(measurements['gyro_x']['dec']**2+
                                                        measurements['gyro_y']['dec']**2+
                                                        measurements['gyro_z']['dec']**2))
               gyro_vector.axis              = (  measurements['gyro_x']['dec']/gyro_magnitude,
                                                  measurements['gyro_y']['dec']/gyro_magnitude,
                                                  measurements['gyro_z']['dec']/gyro_magnitude)
               #admin
               num_packets_ok += 1
               advance_leds('ok',self.serialPortName)
            else:
               num_packets_length_error += 1
               advance_leds('error_length',self.serialPortName)
        except (Tkinter.TclError, ValueError, IndexError):
           err = sys.exc_info()
           print( "Warning (ch. "+str(self.channel)+"): %s (%s) \n" % (str(err[0]), str(err[1])))
           pass
        except:
           err = sys.exc_info()
           print( "Error: %s (%s) \n" % (str(err[0]), str(err[1])))
           self.done = 1
      m.end()
      file.close()
      print(str(num_packets_ok)+           " packets received ok")
      print(str(num_packets_length_error)+ " packets received with length error")
      print(str(num_packets_crc_error)+    " packets received with CRC error")
      num_packets_error = float(num_packets_length_error+num_packets_crc_error)
      sucess_rate = float(num_packets_ok)/float(num_packets_ok+num_packets_error)
      print(str(sucess_rate*100)+"% success rate")
   def quit(self):
      print '\nclosing '+self.serialPortName+" (channel "+str(self.channel)+"):"
      self.done = 1

#====================================== gui  ============================================

channels = [15,20,25,26]
serialPortNames = findSerialPortsNames()

def releaseAndQuit():
   global moteThreadHandlers
   for moteThreadHandler in moteThreadHandlers:
      moteThreadHandler.quit()
      time.sleep(.2)
   root.quit()
   sys.exit()

root=Tkinter.Tk()
root.title("Intersection")
root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
root.resizable(0,0)

connectionCanvas = Tkinter.Canvas(root,width=200,height=250)
temp_y  = 10
for key,serialPortName in enumerate(serialPortNames):
   connectionCanvas.create_text( 65,temp_y  ,text=serialPortName+" (ch. "+str(channels[key])+")",justify=Tkinter.LEFT)
   connectionCanvas.create_text(120,temp_y  ,text="ok",justify=Tkinter.LEFT)
   connectionCanvas.create_oval(150,temp_y- 5,160,temp_y+ 5,tag="led_ok_"          +serialPortName,fill="")
   connectionCanvas.create_oval(165,temp_y- 5,175,temp_y+ 5,tag="led_ok_"          +serialPortName,fill="")
   connectionCanvas.create_text(120,temp_y+15,text="crc",justify=Tkinter.LEFT)
   connectionCanvas.create_oval(150,temp_y+10,160,temp_y+20,tag="led_error_crc_"   +serialPortName,fill="")
   connectionCanvas.create_oval(165,temp_y+10,175,temp_y+20,tag="led_error_crc_"   +serialPortName,fill="")
   connectionCanvas.create_text(120,temp_y+30,text="length",justify=Tkinter.LEFT)
   connectionCanvas.create_oval(150,temp_y+25,160,temp_y+35,tag="led_error_length_"+serialPortName,fill="")
   connectionCanvas.create_oval(165,temp_y+25,175,temp_y+35,tag="led_error_length_"+serialPortName,fill="")
   temp_y += 50
connectionCanvas.configure(height=temp_y)
connectionCanvas.grid(row=0,column=0)

def button_clicked(event):
   guiLock.acquire()
   if (event.widget==car_button):
      file = open("car.activity", 'a')
   elif (event.widget==bike_button):
      file = open("bike.activity", 'a')
   elif (event.widget==pedestrian_button):
      file = open("pedestrian.activity", 'a')
   else:
      print "ERROR unknow button"
   file.write(str(time.time())+" 0\n")
   file.write(str(time.time())+" 1\n")
   file.close()
   guiLock.release()

def button_unclicked(event):
   guiLock.acquire()
   if (event.widget==car_button):
      file = open("car.activity", 'a')
   elif (event.widget==bike_button):
      file = open("bike.activity", 'a')
   elif (event.widget==pedestrian_button):
      file = open("pedestrian.activity", 'a')
   else:
      print "ERROR unknow button"
   file.write(str(time.time())+" 1\n")
   file.write(str(time.time())+" 0\n")
   file.close()
   guiLock.release()

buttonFrame = Tkinter.Frame()

temp_label="car"
car_button = LockEnabledButton(buttonFrame,width=10,height=5,text=temp_label)
temp_lambda = lambda x=temp_label:button_clicked(x)
car_button.bind("<Button-1>"       ,button_clicked)
temp_lambda = lambda x=temp_label:button_unclicked(x)
car_button.bind("<ButtonRelease-1>",temp_lambda)
car_button.grid(row=0,column=0)

temp_label="bike"
bike_button = LockEnabledButton(buttonFrame,width=10,height=5,text=temp_label)
temp_lambda = lambda x=temp_label:button_clicked(x)
bike_button.bind("<Button-1>"       ,temp_lambda)
temp_lambda = lambda x=temp_label:button_unclicked(x)
bike_button.bind("<ButtonRelease-1>",temp_lambda)
bike_button.grid(row=1,column=0)

temp_label="pedestrian"
pedestrian_button = LockEnabledButton(buttonFrame,width=10,height=5,text=temp_label)
temp_lambda = lambda x=temp_label:button_clicked(x)
pedestrian_button.bind("<Button-1>"       ,temp_lambda)
temp_lambda = lambda x=temp_label:button_unclicked(x)
pedestrian_button.bind("<ButtonRelease-1>",temp_lambda)
pedestrian_button.grid(row=2,column=0)

buttonFrame.grid(row=0,column=1)

#====================================== main ============================================

#declare one thread per sniffer
moteThreadHandlers = []
for key,serialPortName in enumerate(serialPortNames):
   moteThreadHandlers.append(moteThread(serialPortName,channels[key]))
#start all threads
for moteThreadHandler in moteThreadHandlers:
   moteThreadHandler.start()

root.mainloop()
