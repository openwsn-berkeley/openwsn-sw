import sys

boiler  = "================================\n"
boiler += "Python installation test script \n"
boiler += "Thomas Watteyne, August 2010    \n"
boiler += "================================"
print boiler

#================== Python

print "\nTesting Python...",
print "works!"

#================== PySerial

print "\nTesting PySerial...",

try:
   import serial
except:
   err = sys.exc_info()
   sys.stderr.write("Error: %s (%s) \n" % (str(err[0]), str(err[1])))
else:
   print "works!"

#================== TkInter

print "\nTesting TkInter...",

def releaseAndQuit():
   root.quit()
   sys.exit()

try:
   import Tkinter
   root=Tkinter.Tk()
   root.title("Testing TkInter")
   root.protocol("WM_DELETE_WINDOW",releaseAndQuit)
   root.resizable(0,0)
except:
   err = sys.exc_info()
   sys.stderr.write("Error: %s (%s) \n" % (str(err[0]), str(err[1])))
else:
   print "works!\n(make sure you can see the window titled \"Testing TkInter\")"

raw_input("\nPress return to close this window...")

