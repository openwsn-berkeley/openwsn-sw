# -*- coding: utf-8 -*-
import usb.core
import usb.util
import time;
 
dev = usb.core.find(idVendor=0x04D8, idProduct=0x000A)
 
if dev is None:
    raise ValueError('Device not found');

#dev.reset();

try:
    dev.set_configuration();
except usb.core.USBError:
    print "Couldn't set configuration (prob b/c of usb->serial driver)"
     
 
cfg = dev.get_active_configuration();
interface_number = cfg[ (2,0) ].bInterfaceNumber

intf = usb.util.find_descriptor( cfg, bInterfaceNumber = interface_number )

ep_out = usb.util.find_descriptor( intf, custom_match = \
                                            lambda e: \
                                                usb.util.endpoint_direction(e.bEndpointAddress) ==\
                                                usb.util.ENDPOINT_OUT )
                                                
ep_in = usb.util.find_descriptor( intf, custom_match = \
                                            lambda e: \
                                                usb.util.endpoint_direction(e.bEndpointAddress) ==\
                                                usb.util.ENDPOINT_IN )                                                

try:
    while(True):
        ep_in.read(64);
        
except usb.core.USBError,e:
    print e


seq_no = 0;

def sendrcv(cmd):
    global seq_no
    seq_no += 1;
    packet = chr((seq_no&0xFF)) + chr((seq_no>>8)&0xFF) + chr(len(cmd))+'\x01\x00'+cmd;
    packet = packet + '\x00'*(64-len(packet))
    #print '-> ['+''.join(['%02X '%ord(i) for i in packet])+']'
    ep_out.write(packet)
    
    dat = ep_in.read(64);
    num_seg = dat[3]
    pay = dat[5:]
   # print '<0- ['+''.join(['%02X '%i for i in dat])+']'
    for i in range(1,num_seg):
        dat = ep_in.read(64);
        if ( i == num_seg-1 ):
            pack_len = 255 % (64-5) + 1;
        else:
            pack_len = 64-5;
        pay += dat[5:pack_len+5]
        #print '<%d- ['%i+''.join(['%02X '%i for i in dat])+']'
        
    return pay

def atob(addr):
    return chr(addr&0xFF) + chr((addr>>8)&0xFF) + chr((addr>>16)&0xFF) +  chr((addr>>24)&0xFF);

addr = 2**22 - 512*4;
rlen = 32;

waddr = 2**22;
wlen = 512*32
'''
nm = 0
sendrcv('\x15'+atob(waddr)+chr(nm)*32)
wpos = waddr
while wpos < waddr + wlen:
    nm+=1;
    sendrcv('\x16'+chr(nm&0xFF)*32)
    wpos += 32
'''
print ' '*11+''.join(['%2d '%i for i in range(0,32)])
while(True):
    time.sleep(.01);
    
    dat = sendrcv('\x10'+atob(addr))
    
    for p in range(0,8):
        print '%10d'%(addr+p*32)+' '+''.join(['%02X '%i for i in dat[p*32 :(p+1)*32 ]])
        
    addr += 256