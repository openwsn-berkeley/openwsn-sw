from Tkinter import *
import serial
import threading

#========================= variables ============================

step=30
num_x_pixels=14
num_y_pixels=14
framecounter=0
isPlaying=False
numTx=0
numRx=1
frames=["33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333\n"]*800
currentframestring_tx = "33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333\n"
currentframestring_rx = "33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333\n"
colors = []
color_codes = []
colors.append("#5F6061")#grey
color_codes.append(0x03)
colors.append("#FF0000")#red
color_codes.append(0x04)
colors.append("#803E00")#brown
color_codes.append(0x05)
colors.append("#000000")#black
color_codes.append(0x06)
colors.append("#810000")#purple
color_codes.append(0x0D)
colors.append("#FFFD0D")#yellow
color_codes.append(0x0E)
colors.append("#FFFFFF")#white
color_codes.append(0x0F)

root=Tk()
root.title("Thrill the World of WSNs")

#========================= helper functions ==========================

def releaseAndQuit():
  root.quit()
  sys.exit()

class serialTx(threading.Thread):
   ser_tx = serial.Serial(port='COM23',baudrate=115200)
   def run(self):
      global currentframestring_tx
      global framecounter
      global numTx
      global numRx
      self.active = True
      while True:
         if self.active==True:
            if self.ser_tx.isOpen()==False:
               self.ser_tx.open()
            try:
               char = self.ser_tx.read(1)
            except:
               err = sys.exc_info()
               sys.stderr.write( "Error serialTx: %s (%s) \n" % (str(err[0]), str(err[1])))         
            else:
               if char=='y':
                  if isPlaying==True:
                     currentframestring_tx=frames[framecounter]
                     #currentframestring_tx=str((numTx/10000)%10)
                     #currentframestring_tx=currentframestring_tx+str((numTx/1000)%10)
                     #currentframestring_tx=currentframestring_tx+str((numTx/100)%10)
                     #currentframestring_tx=currentframestring_tx+str((numTx/10)%10)
                     #currentframestring_tx=currentframestring_tx+str(numTx%10)
                     #currentframestring_tx=currentframestring_tx+"                                                                                              \n"
                  self.ser_tx.write(currentframestring_tx)
                  #displayframe_tx(currentframestring_tx)
                  if isPlaying==True:
                     framecounter=(framecounter+1)%800
                     slider.set(framecounter)
                     currentframetext.delete(1.0,END)
                     currentframetext.insert(END,str(framecounter*0.090)+" sec.")
                     numTx=numTx+1
                     goodputtext.delete(1.0,END)
                     goodputtext.insert(END,str(numRx)+"/"+str(numTx)+"="+str((float(numRx)/float(numTx))*100)+"%")
         else:
            if self.ser_tx.isOpen()==True:
               self.ser_tx.close()

class serialRx(threading.Thread):
   ser_rx = serial.Serial(port='COM21',baudrate=115200)
   def run(self):
      global currentframestring_rx
      global numRx
      state = "WAIT_HEADER"
      numdelimiter = 0
      while True:
         try:
            char = self.ser_rx.read(1)
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error serialRx:%s (%s) \n" % (str(err[0]), str(err[1])))
         else:
            if (state == "WAIT_HEADER"):
               if char == '^':
                  numdelimiter = numdelimiter + 1
               else:
                  numdelimiter = 0
               if (numdelimiter==3):
                  state = "RECEIVING_COMMAND"
                  currentframestring_rx = ""
                  numdelimiter = 0
            else:
               if (state == "RECEIVING_COMMAND"):
                  currentframestring_rx=currentframestring_rx+char
                  if char == '$':
                     numdelimiter = numdelimiter + 1
                  else:
                     numdelimiter = 0
                  if (numdelimiter==3):
                     state = "WAIT_HEADER"
                     numdelimiter = 0
                     currentframestring_rx = currentframestring_rx[:len(currentframestring_rx)-3]
                     if (currentframestring_rx[0]=='D'):
                        currentframestring_rx = currentframestring_rx[1:]
                        numRx=numRx+1
                        displayframe_rx()

def update_currentframestring_tx():
   global currentframestring_tx
   global canvas_tx
   global pixels_t
   currentframestring_tx = ""
   for j in range(0,num_x_pixels):
      for l in range(0,num_y_pixels/2):
         i=2*l
         for k in range(0,len(colors)):
            if canvas_tx.itemcget(pixels_tx[i][j],"fill")==colors[k]:
               current_color_index=k
         code1=color_codes[current_color_index]
         i=2*l+1
         for k in range(0,len(colors)):
            if canvas_tx.itemcget(pixels_tx[i][j],"fill")==colors[k]:
               current_color_index=k
         code2=color_codes[current_color_index]
         char=(code1<<4)+code2
         currentframestring_tx=currentframestring_tx+chr(char)
   currentframestring_tx=currentframestring_tx+'\n'

def displayframe_tx(framestring):
   global canvas_tx
   global currentframestring_tx
   global pixels_tx
   for k in range(0,len(framestring)):
      if k<num_x_pixels*num_y_pixels/2:
         char=ord(framestring[k])
         j=(k*2)/num_x_pixels
         i=(k*2)%num_x_pixels
         code1=(char&0xF0)>>4
         current_color_index_tx=0
         for l in range(0,len(colors)):
            if color_codes[l]==code1:
               current_color_index_tx=l
         canvas_tx.itemconfigure(pixels_tx[i][j],fill=colors[current_color_index_tx])
         j=(k*2)/num_x_pixels
         i=(k*2)%num_x_pixels+1
         code2=char&0x0F
         for l in range(0,len(colors)):
            if color_codes[l]==code2:
               current_color_index_tx=l
         canvas_tx.itemconfigure(pixels_tx[i][j],fill=colors[current_color_index_tx])
   currentframestring_tx=framestring

def displayframe_rx():
   global canvas_rx
   global currentframestring_rx
   global pixels_rx
   for k in range(0,len(currentframestring_rx)):
      if k<num_x_pixels*num_y_pixels/2:
         char=ord(currentframestring_rx[k])
         j=(k*2)/num_x_pixels
         i=(k*2)%num_x_pixels
         code1=(char&0xF0)>>4
         current_color_index_rx=1
         for l in range(0,len(colors)):
            if color_codes[l]==code1:
               current_color_index_rx=l
         try:
            canvas_rx.itemconfigure(pixels_rx[i][j],fill=colors[current_color_index_rx])
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error displayframe_rx 1: %s (%s) \n" % (str(err[0]), str(err[1])))
         j=(k*2)/num_x_pixels
         i=(k*2)%num_x_pixels+1
         code2=char&0x0F
         current_color_index_rx=1
         for l in range(0,len(colors)):
            if color_codes[l]==code2:
               current_color_index_rx=l
         try:
            canvas_rx.itemconfigure(pixels_rx[i][j],fill=colors[current_color_index_rx])
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error displayframe_rx 2: %s (%s) \n" % (str(err[0]), str(err[1])))
   
#========================= row 0 ============================

def printstring():
   update_currentframestring_tx()
   printstring.delete(0,END)
   printstring.insert(0,currentframestring_tx)

printbutton = Button(root,text="print",command=printstring)
printbutton.grid(row=0,column=0)

def displaystring():
   displayframe_tx(printstring.get())

displaybutton = Button(root,text="display",command=displaystring)
displaybutton.grid(row=0,column=1)

def savetofile():
   file = open ( 'thriller.txt', 'w' )
   for framecounter in range(0,800):
      file.write(frames[framecounter])
   file.close()

savebutton = Button(root,text="save",command=savetofile)
savebutton.grid(row=0,column=2)

def keepframeandnext():
   old_frame=frames[framecounter]
   update_currentframestring_tx()
   frames[framecounter]=currentframestring_tx
   temp_counter=framecounter+1
   while (frames[temp_counter]==old_frame) & (temp_counter<800):
      frames[temp_counter]=currentframestring_tx
      temp_counter=temp_counter+1 

keepframeandnextbutton = Button(root,text="keep frame and next",command=keepframeandnext)
keepframeandnextbutton.grid(row=0,column=3)

def keepframe():
   old_frame=frames[framecounter]
   update_currentframestring_tx()
   frames[framecounter]=currentframestring_tx

keepframebutton = Button(root,text="keep frame",command=keepframe)
keepframebutton.grid(row=0,column=4)

#========================= row 1 ============================

printstring=Entry(root,width=num_y_pixels*num_x_pixels/2+2)
printstring.grid(row=1,column=0,columnspan=6)

#========================= row 2 ============================

def recolor(event):
   current_pixel = pixels_tx[event.x/step][event.y/step]
   for i in range(0,len(colors)):
      if canvas_tx.itemcget(current_pixel,"fill")==colors[i]:
         current_color_index=i
   if event.num==1:
      new_color_index=(current_color_index+1)%len(colors)
   elif event.num==2:
      new_color_index=0
   elif event.num==3:
      new_color_index=(current_color_index-1)%len(colors)
   canvas_tx.itemconfigure(current_pixel,fill=colors[new_color_index])
   update_currentframestring_tx()

canvas_tx=Canvas(root,width=num_x_pixels*step,height=num_y_pixels*step)
canvas_tx.bind("<Button-1>",recolor)
canvas_tx.bind("<Button-2>",recolor)
canvas_tx.bind("<Button-3>",recolor)
pixels_tx = []
for i in range(0,num_x_pixels):
   pixels_tx.append([])
   for j in range(0,num_y_pixels):
      pixels_tx[i].append(canvas_tx.create_rectangle(step*i,step*j,step*(i+1),step*(j+1),fill="#5F6061"))
canvas_tx.grid(row=2,column=0,columnspan=3)

canvas_rx=Canvas(root,width=num_x_pixels*step,height=num_y_pixels*step)
pixels_rx = []
for i in range(0,num_x_pixels):
   pixels_rx.append([])
   for j in range(0,num_y_pixels):
      pixels_rx[i].append(canvas_rx.create_rectangle(step*i,step*j,step*(i+1),step*(j+1),fill="#5F6061"))
canvas_rx.grid(row=2,column=3,columnspan=3)

#========================= row 3 ============================

def shiftleft():
   for j in range(0,num_y_pixels):
      for i in range(0,num_x_pixels-1):
         canvas_tx.itemconfigure(pixels_tx[i][j],fill=canvas_tx.itemcget(pixels_tx[i+1][j],"fill"))
      canvas_tx.itemconfigure(pixels_tx[num_x_pixels-1][j],fill=colors[0])
   update_currentframestring_tx()

shiftleftbutton = Button(root,text="shift pixels left",command=shiftleft)
shiftleftbutton.grid(row=3,column=0)

def mirror():
   for j in range(0,num_y_pixels):
      temp_pixelline=[]
      for i in range(num_x_pixels-1,-1,-1):
         temp_pixelline.append(canvas_tx.itemcget(pixels_tx[i][j],"fill"))
      for i in range(0,num_x_pixels):
         canvas_tx.itemconfigure(pixels_tx[i][j],fill=temp_pixelline[i])
   update_currentframestring_tx()

mirrorbutton = Button(root,text="mirror",command=mirror)
mirrorbutton.grid(row=3,column=1)

def clearframe():
   for j in range(0,num_y_pixels):
      for i in range(0,num_x_pixels):
         canvas_tx.itemconfigure(pixels_tx[i][j],fill=colors[0])
   update_currentframestring_tx()

clearbutton = Button(root,text="clear frame",command=clearframe)
clearbutton.grid(row=3,column=2)

def shiftright():
   for j in range(0,num_y_pixels):
      for i in range(num_x_pixels-1,0,-1):
         canvas_tx.itemconfigure(pixels_tx[i][j],fill=canvas_tx.itemcget(pixels_tx[i-1][j],"fill"))
      canvas_tx.itemconfigure(pixels_tx[0][j],fill=colors[0])
   update_currentframestring_tx()

shiftrightbutton = Button(root,text="shift pixels right",command=shiftright)
shiftrightbutton.grid(row=3,column=3)

#========================= row 4 ============================

def play():
   global isPlaying
   global numTx
   global numRx
   isPlaying=True
   numTx=0
   numRx=0
   displayframe_tx("C333334433333C3C3334334333C333C34333343C33333D333333D3333343C3333C343334333C33C33343433333CC333334\n")

playbutton = Button(root,text="play",command=play)
playbutton.grid(row=4,column=0)

def stop():
   global isPlaying
   isPlaying=False
   displayframe_tx(currentframestring_tx)

playbutton = Button(root,text="stop",command=stop)
playbutton.grid(row=4,column=1)

def gotoframe(event):
   global framecounter
   framecounter=slider.get()
   displayframe_tx(frames[framecounter])

slider = Scale(root, from_=0, to=799, orient=HORIZONTAL,length=num_x_pixels*step-10)
slider.bind("<B1-Motion>",gotoframe)
slider.bind("<ButtonRelease-1>",gotoframe)
slider.grid(row=4,column=2,columnspan=3)

goodputtext = Text(root,borderwidth=0,height=1,width=20)
goodputtext.grid(row=4,column=5)

#========================= row 5 ============================

def shiftearlier():
   global framecounter
   if framecounter>0:
      for i in range(framecounter,800):
         frames[i-1]=frames[i]

shiftearlierbutton = Button(root,text="this frame earlier",command=shiftearlier)
shiftearlierbutton.grid(row=5,column=0)

currentframetext = Text(root,borderwidth=0,height=1,width=30)
currentframetext.grid(row=5,column=1,columnspan=2)

def shiftlater():
   global framecounter
   for i in range(798,framecounter-1,-1):
      frames[i+1]=frames[i]

shiftlaterbutton = Button(root,text="this frame later",command=shiftlater)
shiftlaterbutton.grid(row=5,column=3)

#========================= main ============================

root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
framecounter=0
file = open ( 'thriller.txt', 'r' )
temp_frame = file.readline()
while (temp_frame!='') & (temp_frame!='\n'):
   frames[framecounter]=temp_frame
   framecounter=framecounter+1
   temp_frame = file.readline()
file.close()
framecounter=0
serialtx=serialTx()
serialtx.start()
serialrx=serialRx()
serialrx.start()
root.mainloop()
