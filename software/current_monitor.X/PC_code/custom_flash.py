# -*- coding: utf-8 -*-
import usb.core
import usb.util
import time;
 
dev = usb.core.find(idVendor=0x04D8, idProduct=0x000A)
 
if dev is None:
    raise ValueError('Device not found');
 
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
                                                
seq_no = 0;

def sendrcv(cmd):
    global seq_no
    seq_no += 1;
    packet = chr((seq_no&0xFF)) + chr((seq_no>>8)&0xFF) + chr(len(cmd))+'\x01\x00'+cmd;
    packet = packet + '\x00'*(64-len(packet))
    #print '-> ['+''.join(['%02X '%ord(i) for i in packet])+']'
    ep_out.write(packet)
    dat = ep_in.read(64);
    return dat

def atob(addr):
    return chr(addr&0xFF) + chr((addr>>8)&0xFF) + chr((addr>>16)&0xFF) +  chr((addr>>24)&0xFF);

addr = 0;
rlen = 32;

waddr = 512*8;
wlen = 512

sendrcv('\x15'+atob(waddr)+atob(wlen)+'\xAA'*32)
wpos = waddr
while wpos < waddr + wlen:
    sendrcv('\x16'+'\xAA'*32)
    wpos += 32

while(True):
    time.sleep(.01);
    seq_no += 1;
    
    dat = sendrcv('\x10'+atob(addr)+atob(rlen))

    #print '<- ['+''.join(['%02X '%i for i in dat])+']'
    print '%10d'%addr+' '+''.join(['%02X '%i for i in dat[5:5+32]])
    addr += 32