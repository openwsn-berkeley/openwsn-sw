elements["videoSource"]=StringVar()

#--videoSource
   elements[serialport]["commands"]["videoSourceRadiobutton"]=Radiobutton(elements[serialport]["commands"]["frame"],
         text="videoSource",variable=elements["videoSource"],value=serialport)
   elements[serialport]["commands"]["videoSourceRadiobutton"].grid(row=1,column=6)

ACTIVATE_CAMERA =  FALSE
SENDING_NODE    = '0x2'

if (ACTIVATE_CAMERA):
   if os.name=='nt':
      webcam = Device()
      webcam.setResolution(RESOLUTION_X,RESOLUTION_Y)

displayImageEvent = threading.Event()
takeImageEvent    = threading.Event()

#================================= image ============================

class takeImageThread(threading.Thread):
   active=True
   def run(self):
      while self.active:
         if os.name=='nt':
            takeImageEvent.wait()
            image = webcam.getImage()                  
            image = ImageOps.grayscale(image)
            image.save('temp_tx.jpg',quality=30)
            print '_CAM_',
            takeImageEvent.clear()

         elif os.name=='posix':
            takeImageEvent.wait()
            print "thomas"
            capture = highgui.cvCreateCameraCapture(0)
            # set the wanted image size from the camera
            highgui.cvSetCaptureProperty(capture, highgui.3,160)
            highgui.cvSetCaptureProperty(capture, highgui.4,120)
            highgui.cvSetCaptureProperty(capture, 10, 0.8)
            pygame.init()
            im = highgui.cvQueryFrame(capture)
    
            # Add the line below if you need it (Ubuntu 8.04+)
            im = opencv.cvGetMat(im)
            time.sleep(0.1)
            #convert Ipl image to PIL image
            highgui.cvSaveImage("temp_tx.jpg", im)
            im = highgui.cvLoadImage("temp_tx.jpg",0)
            highgui.cvSaveImage("temp_tx.jpg", im)
            os.system("convert -resize 40% -quality 75 temp_tx.jpg temp_tx.jpg")
            print '_CAM_',
            takeImageEvent.clear()

def sendImage(serialport):
   if elements[serialport]["image"]["packet_rank_in_frame"]==elements[serialport]["image"]["number_packets_in_frame"]:
      elements[serialport]["image"]["payloads"] = []
      file_tx = open ( 'temp_tx.jpg', 'rb' )
      #file_tx = open ( 'test_tx.txt', 'rb' )
      while True:
         temp_payload = file_tx.read(PAYLOAD_SIZE-4)
         if len(temp_payload)==0:
            break
         while len(temp_payload)<PAYLOAD_SIZE-4:
            temp_payload = temp_payload+'0'
         elements[serialport]["image"]["payloads"].append(temp_payload)
      file_tx.close()
      #print "Tx ("+str(len(elements[serialport]["image"]["payloads"]))+"):"
      #print elements[serialport]["image"]["payloads"]
      if (ACTIVATE_CAMERA):
         takeImageEvent.set()
      elements[serialport]["image"]["frame_counter"]           = (elements[serialport]["image"]["frame_counter"]+1)%256
      elements[serialport]["image"]["number_packets_in_frame"] = len(elements[serialport]["image"]["payloads"])
      elements[serialport]["image"]["packet_rank_in_frame"]    = 0
   payloadToTransmit=chr(elements[serialport]["image"]["frame_counter"])+\
                     chr(elements[serialport]["image"]["number_packets_in_frame"])+\
                     chr(elements[serialport]["image"]["packet_rank_in_frame"])+\
                     elements[serialport]["image"]["payloads"][elements[serialport]["image"]["packet_rank_in_frame"]]
   serialport_handlers[serialport].write(payloadToTransmit)
   elements[serialport]["image"]["packet_rank_in_frame"] += 1

def recordImage(serialport,input):
   input = input[3:len(input)-1]
   if (len(input)!=PAYLOAD_SIZE-1):
      try:
         tkSemaphore.acquire()
         errorTextHeader()
         errorText.insert(END,"input too short to be a recordImage ("+str(len(input))+" chars)\n")
         tkSemaphore.release()
      except:
         print "ERROR 1"
         err = sys.exc_info()
         sys.stderr.write( "Error recordImage 1: %s (%s) \n" % (str(err[0]), str(err[1])))
      return
   previous_frame_counter_rx   = elements[serialport]["image"]["frame_counter"]
   elements[serialport]["image"]["frame_counter"]            = ord(input[0])
   elements[serialport]["image"]["number_packets_in_frame"]  = ord(input[1])
   elements[serialport]["image"]["packet_rank_in_frame"]     = ord(input[2])
   if (elements[serialport]["image"]["packet_rank_in_frame"]==math.ceil(elements[serialport]["image"]["number_packets_in_frame"]/2)):
      displayImageEvent.set()
   if (elements[serialport]["image"]["frame_counter"] != previous_frame_counter_rx):
      #print "Rx ("+str(len(elements[serialport]["image"]["payloads"]))+"):"
      #print elements[serialport]["image"]["payloads"]
      ## store image in file and display
      if (previous_frame_counter_rx!=-1):
         file_rx = open ( 'temp_rx.jpg', 'wb' )
         #file_rx = open ( 'test_rx.txt', 'wb' )
         for i in range(0,len(elements[serialport]["image"]["payloads"])):
            file_rx.write(elements[serialport]["image"]["payloads"][i])
         file_rx.close
         #print "\nframe "+str(elements[serialport]["image"]["frame_counter"])+": ",
      ## reset the payload_rx buffer
      temp_string = ""
      for i in range(0,PAYLOAD_SIZE):
         temp_string = temp_string+'0'
      elements[serialport]["image"]["payloads"] = [temp_string]*elements[serialport]["image"]["number_packets_in_frame"]
   if (elements[serialport]["image"]["packet_rank_in_frame"]<elements[serialport]["image"]["number_packets_in_frame"]) &\
      (elements[serialport]["image"]["packet_rank_in_frame"]<len(elements[serialport]["image"]["payloads"])):
         elements[serialport]["image"]["payloads"][elements[serialport]["image"]["packet_rank_in_frame"]]=input[3:len(input)]
         #print str(elements[serialport]["image"]["payloads"][elements[serialport]["image"]["packet_rank_in_frame"]]),

class displayImageThread(threading.Thread):
   active=True
   def run(self):
      while self.active:
         displayImageEvent.wait()
         rxImageCanvas.delete(ALL)
         os.system("killall eog")
         try:
            if os.name=='nt':
               image_rx = Image.open("temp_rx.jpg")
               image_rx = image_rx.resize((RX_IMAGE_WIDTH,RX_IMAGE_HEIGHT))
               #image_rx = image_rx.filter(ImageFilter.SMOOTH_MORE)
               photo_rx = ImageTk.PhotoImage(image_rx)
               rxImageCanvas.create_image(RX_IMAGE_WIDTH/2,RX_IMAGE_HEIGHT/2,image=photo_rx)
            elif os.name=='posix':
               os.system("eog temp_rx.jpg")


         except:
            err = sys.exc_info()
            sys.stderr.write( "Error displayImageThread: %s (%s) \n" % (str(err[0]), str(err[1])))
            print '_ERROR_',
         else:
            print '_OK_',
         displayImageEvent.clear()

#imageWindow=Toplevel()
#imageWindow.title("OpenLiveView")
#imageWindow.protocol("WM_DELETE_WINDOW",releaseAndQuit)
#imageWindow.resizable(0,0)
#rxImageCanvas=Canvas(imageWindow,width=RX_IMAGE_WIDTH,height=RX_IMAGE_HEIGHT)
#rxImageCanvas.grid(row=0,column=0)

stopVideoButton = Button(leftFrame,text="stopVideo",command=stopVideo)
stopVideoButton.grid(row=3,column=1)

#image
   elements[serialport]["image"] = {}
   elements[serialport]["image"]["frame_counter"]           = 0
   elements[serialport]["image"]["number_packets_in_frame"] = 0
   elements[serialport]["image"]["packet_rank_in_frame"]    = 0
   elements[serialport]["image"]["payloads"]                = []

takeimagethread=takeImageThread()
takeimagethread.start()
displayimagethread=displayImageThread()
displayimagethread.start()


def stopVideo():
   elements["videoSource"].set("NULL")
   for serialport in serialport_names:
      elements[serialport]["commands"]["videoSourceRadiobutton"].deselect()
