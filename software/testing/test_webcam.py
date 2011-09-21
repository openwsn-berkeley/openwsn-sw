from Tkinter import *
from PIL import Image, ImageTk, ImageOps
from VideoCapture import Device
import threading, os, time

photo_display_height=480
photo_display_width=640
cam = Device()
cam.setResolution(160,120)
#cam.setResolution(640,480)
root=Tk()

def releaseAndQuit():
   #os.remove('temp_color.jpg')
   #os.remove('temp_gray.jpg')
   root.quit()
   sys.exit()

class Video(threading.Thread):
   def run(self):
      imagecounter=0;
      while True:
         time.sleep(0.5)
         imagecounter+=1
         image = cam.getImage()
         image.save('temp/color_'+str(imagecounter)+'.jpg',quality=100)
         image = ImageOps.grayscale(image)
         image.save('temp/gray_'+str(imagecounter)+'.jpg',quality=100)
         sizetext.delete(1.0,END)
         sizetext.insert(END,"color: "+str( os.path.getsize('temp/color_'+str(imagecounter)+'.jpg'))+\
               " bytes, grayscale: "+str( os.path.getsize('temp/gray_'+str(imagecounter)+'.jpg')))
         try:
            photo_display_size=640,480
            image_rx = Image.open('temp/color_'+str(imagecounter)+'.jpg')
            image_rx = image_rx.resize((photo_display_width,photo_display_height))
            photo_rx = ImageTk.PhotoImage(image_rx)
            canvas_rx.create_image(photo_display_width/2,photo_display_height/2,image=photo_rx)
         except:
            err = sys.exc_info()
            sys.stderr.write( "Error opening image: %s (%s) \n" % (str(err[0]), str(err[1])))

root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
canvas_rx=Canvas(root,width=photo_display_width,height=photo_display_height)
canvas_rx.grid(row=0,column=0)
sizetext = Text(root,borderwidth=0,height=1,width=50)
sizetext.grid(row=1,column=0)
video=Video()
video.start()
root.mainloop()
