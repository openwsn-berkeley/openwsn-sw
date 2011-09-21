from Tkinter import *
from PIL import Image, ImageTk, ImageOps, ImageFilter
from VideoCapture import Device
import serial, threading, os, math, time

#========================= variables ============================

display_height=600
display_width=800
payload_size=93
cam = Device()
cam.setResolution(160,120)
numTx=0
numRx=1
displayImageEvent = threading.Event()
takeImageEvent = threading.Event()

#========================= helper functions ==========================

def releaseAndQuit():
   takeImage.active=False
   serialtx.active=False
   serialrx.active=False
   displayimage.active=False
   time.sleep(.1)
   root.quit()
   sys.exit()

class takeImage(threading.Thread):
   active=True
   def run(self):
      while self.active:
         takeImageEvent.wait()
         image = cam.getImage()                  
         image = ImageOps.grayscale(image)
         image.save('temp_tx.jpg',quality=30)
         print '_CAM_',
         takeImageEvent.clear()

class txMoteThread(threading.Thread):
   active=True
   ser_tx = serial.Serial(port='COM23',baudrate=115200)
   def run(self):
      global numTx
      global numRx
      state = "WAIT_HEADER"
      numdelimiter = 0
      frame_counter_tx           = 0
      packet_rank_in_frame_tx    = 0
      number_packets_in_frame_tx = 0
      payloadToTransmit=""
      payloads_tx = []
      while self.active:
            try:
               char = self.ser_tx.read(1)
            except:
               err = sys.exc_info()
               sys.stderr.write( "Error txMoteThread: %s (%s) \n" % (str(err[0]), str(err[1])))
            else:
               if (state == "WAIT_HEADER"):
                  if char == '^':
                     numdelimiter += 1
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
                        numdelimiter += 1
                     else:
                        numdelimiter = 0
                     if (numdelimiter==3):
                        state = "WAIT_HEADER"
                        numdelimiter = 0
                        input = input.rstrip('$')
                        if input[0]=='C':      #this is a request for data
                           if packet_rank_in_frame_tx==number_packets_in_frame_tx:
                              print str(ord(input[1])),
                              payloads_tx = []
                              file_tx = open ( 'temp_tx.jpg', 'rb' )
                              #file_tx = open ( 'test_tx.txt', 'rb' )
                              while True:
                                 temp_payload = file_tx.read(payload_size-4)
                                 if len(temp_payload)==0:
                                    break
                                 while len(temp_payload)<payload_size-4:
                                    temp_payload = temp_payload+'0'
                              payloads_tx.append(temp_payload)
                              file_tx.close()
                             #poipoitakeImageEvent.set()
                              frame_counter_tx           = (frame_counter_tx + 1)%256
                              number_packets_in_frame_tx = len(payloads_tx)
                              packet_rank_in_frame_tx    = 0
                           payloadToTransmit='_'+\
                                             chr(frame_counter_tx)+\
                                             chr(number_packets_in_frame_tx)+\
                                             chr(packet_rank_in_frame_tx)+\
                                             payloads_tx[packet_rank_in_frame_tx]
                           self.ser_tx.write(payloadToTransmit)
                           packet_rank_in_frame_tx += 1
                           numTx += 1
                           goodputtext.delete(1.0,END)
                           goodputtext.insert(END,str(numRx)+"/"+str(numTx)+"="+str((float(numRx)/float(numTx))*100)+"%")
                           txpacketcountertext.delete(1.0,END)
                           txpacketcountertext.insert(END,"Tx frame "+str(frame_counter_tx)+
                                                          ": packet "+str(packet_rank_in_frame_tx)+
                                                          "/"+str(number_packets_in_frame_tx))

class rxMoteThread(threading.Thread):
   active=True
   payloadLastReceived = ""
   ser_rx = serial.Serial(port='COM22',baudrate=115200)
   def run(self):
      global numRx
      state = "WAIT_HEADER"
      numdelimiter = 0
      frame_counter_rx           = -1
      packet_rank_in_frame_rx    =  0
      number_packets_in_frame_rx =  0
      payloads_rx = []
      while self.active:
         try:
            char = self.ser_rx.read(1)
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error rxMoteThread: %s (%s) \n" % (str(err[0]), str(err[1])))
         else:
            if (state == "WAIT_HEADER"):
               if char == '^':
                  numdelimiter += 1
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
                     numdelimiter += 1
                  else:
                     numdelimiter = 0
                  if (numdelimiter==3):
                     state = "WAIT_HEADER"
                     numdelimiter = 0
                     input = input.rstrip('$')
                     if input[0]=='D':      #this is a data packet
                        file_rx = open ( 'temp_rx.txt', 'ab' )
                        for i in range(5,len(input)-1):
                           file_rx.write(input[i])
                        file_rx.close
                        payloadLastReceived = input[2:len(input)-1]
                        #receive the image
                        if (len(payloadLastReceived)==payload_size):
                            numRx=numRx+1
                            previous_frame_counter_rx   = frame_counter_rx
                            frame_counter_rx            = ord(payloadLastReceived[1])
                            number_packets_in_frame_rx  = ord(payloadLastReceived[2])
                            packet_rank_in_frame_rx     = ord(payloadLastReceived[3])
                            #poipoiif (packet_rank_in_frame_rx==math.ceil(number_packets_in_frame_rx/2)):
                               #displayImageEvent.set()
                            if (frame_counter_rx != previous_frame_counter_rx):
                               ## store image in file and display
                               if previous_frame_counter_rx!=-1:
                                  file_rx = open ( 'temp_rx.jpg', 'wb' )
                                  #file_rx = open ( 'temp_rx.txt', 'wb' )
                                  for i in range(0,len(payloads_rx)):
                                     file_rx.write(payloads_rx[i])
                                  file_rx.close
                                  print "\nframe "+str(frame_counter_rx)+": ",
                               ## reset the payload_rx buffer
                               temp_string = ""
                               for i in range(0,payload_size):
                                  temp_string = temp_string+'0'
                               payloads_rx = [temp_string]*number_packets_in_frame_rx
                            if (packet_rank_in_frame_rx<number_packets_in_frame_rx) &\
                               (packet_rank_in_frame_rx<len(payloads_rx)):
                                  payloads_rx[packet_rank_in_frame_rx]=payloadLastReceived[4:len(payloadLastReceived)-1]
                                  print str(packet_rank_in_frame_rx),
                            rxpacketcountertext.delete(1.0,END)
                            rxpacketcountertext.insert(END,"Rx frame "+str(frame_counter_rx)+
                                                           ": packet "+str(packet_rank_in_frame_rx)+
                                                           "/"+str(number_packets_in_frame_rx))

class displayImage(threading.Thread):
   active=True
   def run(self):
      while self.active:
         displayImageEvent.wait()
         try:
            image_rx = Image.open("temp_rx.jpg")
            image_rx = image_rx.resize((display_width,display_height))
            #image_rx = image_rx.filter(ImageFilter.SMOOTH_MORE)
            photo_rx = ImageTk.PhotoImage(image_rx)
            canvas_rx.create_image(display_width/2,display_height/2,image=photo_rx)
         except:
            print '_ERROR_',
         else:
            print '_OK_',
         displayImageEvent.clear()

#========================= main ============================

##window
root=Tk()
root.title("Poipoi!")
root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
canvas_rx=Canvas(root,width=display_width,height=display_height)
canvas_rx.grid(row=0,column=0,columnspan=3)
txpacketcountertext = Text(root,borderwidth=0,height=1,width=30)
txpacketcountertext.grid(row=1,column=0)
goodputtext = Text(root,borderwidth=0,height=1,width=30)
goodputtext.grid(row=1,column=1)
rxpacketcountertext = Text(root,borderwidth=0,height=1,width=30)
rxpacketcountertext.grid(row=1,column=2)
##transmitter
takeimage=takeImage()
takeimage.start()
serialtx=txMoteThread()
serialtx.start()
##receiver
serialrx=rxMoteThread()
serialrx.start()
displayimage=displayImage()
displayimage.start()
##main
root.mainloop()
