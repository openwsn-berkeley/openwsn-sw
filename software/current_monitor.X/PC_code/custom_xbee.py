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
    packet = chr((seq_no&0xFF)) + chr((seq_no>>8)&0xFF) + '\x01\x01\x00'+cmd;
    packet = packet + '\x00'*(64-len(packet))
    ep_out.write(packet)
    dat = ep_in.read(64);
    return dat

sendrcv('\x24');

while(True):
    time.sleep(.1);
    seq_no += 1;
    dat = sendrcv('\x26')

    #print ''.join([' %02X'%i for i in dat])
    commands = dat[5]
    overflow = dat[6]
    
    print "Commands: %d, Overflow: %d"%(commands,overflow)
    pos = 7;
    for i in range(0,commands):
        alen = dat[pos+2]
        vstr = ''
        for j in range(0,alen):
            vstr += '%02X'%(dat[pos+3+j])
        print "\t%c%c %d %s"%(dat[pos],dat[pos+1],alen,vstr)
        pos += 3 + alen;