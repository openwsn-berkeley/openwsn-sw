import sys
import objc
import serial
import threading
import datetime
from _uicaboodle import UIApplicationMain
from objc import YES, NO, NULL

objc.loadBundle("UIKit", globals(), "/System/Library/Frameworks/UIKit.framework")

WKP_GINA_UDP_HELI    = 2192
WKP_SCRIPT_UDP_HELI  = 8082

IPV6PREFIX   = '2001:0470:846d:1'
IP64B_PREFIX = ''.join(['\x20','\x01','\x04','\x70','\x84','\x6d','\x00','\x01'])

status_file = open('/var/mobile/OpenWSN.app.log','a')
sys.stderr = status_file
sys.stdout = status_file

#================================= global variables =====================================

moteThread_active  = 1

serialHandler      = ''

dataToSend         = ''
dataToSendLock     = threading.Lock()
guiLock            = threading.Lock()

#================================= moteThread ===========================================

def output_status(message):
   sys.stderr.write(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")+" "+message+"\n")
   sys.stderr.flush()

class moteThread(threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
   def run(self):
      global serialHandler,moteThread_active, guiLock
      output_status("STATUS [moteThread] starting")
      while True:
         try:
            serialHandler = serial.Serial('/dev/tty.iap',baudrate=115200,timeout=5)
         except:
            err = sys.exc_info()
            output_status("ERROR [moteThread] 1: "+str(err[0])+" ("+str(err[1])+")")
         else:
            output_status("STATUS [moteThread] moteThread connected to "+serialHandler.portstr)
            dataToSendLock.acquire()
            dataToSend = ''
            dataToSendLock.release()
            state = "WAIT_HEADER"
            numdelimiter = 0
            while True:
               if (moteThread_active==0):
                  output_status("WARNING [moteThread]: 'moteThread exiting.")
                  return
               try:
                  char = serialHandler.read(1)
               except SystemExit:
                  return
               except:
                  err = sys.exc_info()
                  output_status("ERROR [moteThread] 2: "+str(err[0])+" ("+str(err[1])+")")
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
                              output_status("ERROR [moteThread] 3: "+str(err[0])+" ("+str(err[1])+")")
                              pass
     
def parseInput(input):
   global dataToSend, dataToSendLock, disable_bridge, guiLock
   #byte 0 is the type of status message
   if (input[0]=="R"):   #waiting for command
      if (ord(input[1])==200):  #input buffer empty
         dataToSendLock.acquire()
         if (len(dataToSend)>0):
            output_status("POIPOI [parseInput] send data")
            serialHandler.write('D')
            serialHandler.write(chr(len(dataToSend)))
            serialHandler.write(dataToSend)
            dataToSend = ''
         else:
            output_status("POIPOI [parseInput] activate basestation")
            serialHandler.write('B')
            serialHandler.write(chr(1+len(IP64B_PREFIX)))
            serialHandler.write('Y')
            serialHandler.write(IP64B_PREFIX)
         dataToSendLock.release()

#================================= heli send command ====================================

def heli_send_command():
   global motor1_value, motor2_value
   try:
      #send the command over udp_proxy
      heli_command = []
      heli_command.append(chr(int(motor1_value/256)))
      heli_command.append(chr(int(motor1_value%256)))
      heli_command.append(chr(int(motor2_value/256)))
      heli_command.append(chr(int(motor2_value%256)))
      heli_command = ''.join(heli_command)
      udp_proxy_send(heli_command,WKP_SCRIPT_UDP_HELI,WKP_GINA_UDP_HELI)
   except:
      err = sys.exc_info()
      output_status("ERROR heli_send_command: %s (%s) \n" % (str(err[0]), str(err[1])))

#================================= UDP proxy ============================================

def udp_proxy_send(udp_payload_to_send,udp_source_port,udp_destination_port):
   global dataToSend, dataToSendLock, guiLock
   global connectionType
   try:
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
      #compress IPv6 packet using 6LoWPAN
      lowpan_pkt = ipv6_to_lowpan(ipv6_pkt_disassambled, IPHC_TF_ELIDED, IPHC_NH_INLINE, IPHC_HLIM_INLINE, \
                                  IPHC_CID_NO, IPHC_SAC_STATELESS, IPHC_SAM_ELIDED, IPHC_M_NO, \
                                  IPHC_DAC_STATELESS, IPHC_DAM_ELIDED)
      #retrieve next hop and send
      nextHop_string = '20010470846d000114159209022b0033'
      nextHop_string = nextHop_string[16:]
      nextHop = ''
      for i in range(0,8):
         nextHop += chr(int(nextHop_string[2*i:2*i+2],16))
      dataToSendLock.acquire()
      dataToSend = nextHop + lowpan_pkt
      dataToSendLock.release()
   except:
      err = sys.exc_info()
      output_status("ERROR udp_proxy_send: %s (%s) \n" % (str(err[0]), str(err[1])))

#================================= 6LoWPAN ==============================================

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
      output_status("ERROR [ipv6_to_lowpan] unsupported tf==IPHC_TF_4B")
      pass
   elif (tf == IPHC_TF_1B):
      output_status("ERROR [ipv6_to_lowpan] unsupported tf==IPHC_TF_1B")
      pass
   else:
      output_status("ERROR [ipv6_to_lowpan] wrong tf=="+str(tf))
      pass
   # nh
   if (nh == IPHC_NH_INLINE):
      pkt_lowpan.append(chr(pkt_ipv6['next_header']))
   elif (nh == IPHC_NH_COMPRESSED):
      output_status("ERROR [ipv6_to_lowpan] unsupported nh==IPHC_NH_COMPRESSED")
      pass
   else:
      output_status("ERROR [ipv6_to_lowpan] wrong nh=="+str(nh))
   # hlim
   if (hlim == IPHC_HLIM_INLINE):
      pkt_lowpan.append(chr(pkt_ipv6['hop_limit']))
   # IPHC_HLIM1,64,255 unsupported
   else:
      output_status("ERROR [ipv6_to_lowpan] wrong hlim=="+str(hlim))
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
      output_status("ERROR [ipv6_to_lowpan] wrong sam=="+str(sam))
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
      output_status("ERROR [ipv6_to_lowpan] wrong dam=="+str(dam))
   # payload
   for i in range(0,len(pkt_ipv6['payload'])):
      pkt_lowpan.append(pkt_ipv6['payload'][i])
   # join
   pkt_lowpan = ''.join(pkt_lowpan)
   return pkt_lowpan

#================================= UIApplication ========================================

class Application(UIApplication):

   def slider_moved(self, sender):
      global motor1_value, motors_value, motor2_value
      try:
         #update slider positions
         if   (sender==self.motor1_slider):
            self.motors_slider.setValue_((self.motor1_slider.value()+self.motor2_slider.value())/2)
         elif (sender==self.motors_slider):
            if (self.motors_slider.value()==100):
               self.motor1_slider.setValue_(100)
               self.motor2_slider.setValue_(100)
            elif (self.motors_slider.value()==0):
               self.motor1_slider.setValue_(0)
               self.motor2_slider.setValue_(0)
            else:
               difference = self.motors_slider.value()-motors_value
               self.motor1_slider.setValue_(self.motor1_slider.value()+difference)
               self.motor2_slider.setValue_(self.motor2_slider.value()+difference)
         elif (sender==self.motor2_slider):
            self.motors_slider.setValue_((self.motor1_slider.value()+self.motor2_slider.value())/2)
         #record slider positions
         motor1_value = self.motor1_slider.value()
         motors_value = self.motors_slider.value()
         motor2_value = self.motor2_slider.value()
         #send heli command over serial port
         heli_send_command()
      except:
         err = sys.exc_info()
         output_status("ERROR slider_moved: %s (%s) \n" % (str(err[0]), str(err[1])))

   @objc.signature("v@:@")
   def applicationDidFinishLaunching_(self, unused):
      global motor1_value, motors_value, motor2_value

      output_status("STATUS [UIApplication] starting")
      
      # UIWindow and UIView
      self.window = UIWindow.alloc().initWithFrame_(UIHardware.fullScreenApplicationContentRect())
      self.window.orderFront_(self)
      self.window.makeKey_(self)
      self.window.setHidden_(NO)
      self.view   = UIView.alloc().initWithFrame_(self.window.bounds())
      self.window.setContentView_(self.view)

      # UINavigationBar
      self.navbar = UINavigationBar.alloc().initWithFrame_(((0,0), (self.window.bounds()[1][0], UINavigationBar.defaultSize()[1])));
      self.navbar.setBarStyle_(1)
      self.navbar.setDelegate_(self)
      self.navbar.enableAnimation()
      self.navbar.pushNavigationItem_(UINavigationItem.alloc().initWithTitle_("OpenWSN"))
      self.view.addSubview_(self.navbar)

      # UISlider
      self.motor1_slider = UISlider.alloc().initWithFrame_( ((30,80),(250,100)) )
      self.motor1_slider.setMinimumValue_(0)
      self.motor1_slider.setMaximumValue_(100)
      self.motor1_slider.setValue_(0)
      self.motor1_slider.setContinuous_(NO)
      self.motor1_slider.addTarget_action_forControlEvents_(self, self.slider_moved, 4096)
      self.view.addSubview_(self.motor1_slider)
      motor1_value = self.motor1_slider.value()

      self.motors_slider = UISlider.alloc().initWithFrame_( ((30,180),(250,100)) )
      self.motors_slider.setMinimumValue_(0)
      self.motors_slider.setMaximumValue_(100)
      self.motors_slider.setValue_(0)
      self.motors_slider.setContinuous_(NO)
      self.motors_slider.addTarget_action_forControlEvents_(self, self.slider_moved, 4096)
      self.view.addSubview_(self.motors_slider)
      motors_value = self.motors_slider.value()

      self.motor2_slider = UISlider.alloc().initWithFrame_( ((30,280),(250,100)) )
      self.motor2_slider.setMinimumValue_(0)
      self.motor2_slider.setMaximumValue_(100)
      self.motor2_slider.setValue_(0)
      self.motor2_slider.setContinuous_(NO)
      self.motor2_slider.addTarget_action_forControlEvents_(self, self.slider_moved, 4096)
      self.view.addSubview_(self.motor2_slider)
      motor2_value = self.motor2_slider.value()

moteThreadHandler = moteThread()
moteThreadHandler.start()
UIApplicationMain(sys.argv, Application)

'''
def button_clicked(self, sender):
if   (sender==self.up_button):
message = 'Up'
elif (sender==self.left_button):
message = 'Left'
elif (sender==self.right_button):
message = 'Right'
else:
message = 'Down'
alertView = UIAlertView.alloc().initWithTitle_message_delegate_cancelButtonTitle_otherButtonTitles_(str(sender.buttonType),message, self, "OK", None)
alertView.show()
# UIButton
try:
self.up_button      = UIButton.alloc().initWithFrame_(((120,100),(100,100)))
self.up_button.setTitle_forState_('Up',0)
self.up_button.addTarget_action_forControlEvents_(self,self.button_clicked,1) 
self.up_button.setEnabled_(YES)
self.view.addSubview_(self.up_button)
self.left_button    = UIButton.alloc().initWithFrame_((( 0,200),(100,100)))
self.left_button.setTitle_forState_('Left',0)
self.left_button.addTarget_action_forControlEvents_(self,self.button_clicked,1) 
self.left_button.setEnabled_(YES)
self.view.addSubview_(self.left_button)
self.right_button   = UIButton.alloc().initWithFrame_(((220,200),(100,100)))
self.right_button.setTitle_forState_('Right',0)
self.right_button.addTarget_action_forControlEvents_(self,self.button_clicked,1) 
self.right_button.setEnabled_(YES)
self.view.addSubview_(self.right_button)
self.down_button    = UIButton.alloc().initWithFrame_(((120,300),(100,100)))
self.down_button.setTitle_forState_('Down',0)
self.down_button.addTarget_action_forControlEvents_(self,self.button_clicked,1) 
self.down_button.setEnabled_(YES)
self.view.addSubview_(self.down_button)
except:
err = sys.exc_info()
alertView = UIAlertView.alloc().initWithTitle_message_delegate_cancelButtonTitle_otherButtonTitles_("title","message", self, "OK", None)
alertView.setMessage_("Error: %s (%s) \n" % (str(err[0]), str(err[1])))
alertView.show()

# UIAlertView (alert window in the middle of the screen)
alertView = UIAlertView.alloc().initWithTitle_message_delegate_cancelButtonTitle_otherButtonTitles_("title","message", self, "button", None)
alertView.setTitle_("title")
alertView.setMessage_("message")
alertView.show()

# UIActionSheet (which appears from the bottom of the screen)
actionSheet = UIActionSheet.alloc().initWithTitle_delegate_cancelButtonTitle_destructiveButtonTitle_otherButtonTitles_("title", self, "cancel", "destruct", None)
actionSheet.showInView_(self.view)'''
