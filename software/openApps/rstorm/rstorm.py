import os
import sys
from Tkinter import *
import tkMessageBox
import re
import time
import struct

p = os.path.dirname(sys.argv[0])
p = os.path.join(p,'..','..','..','..','coap')
p = os.path.abspath(p)
sys.path.insert(0,p)

from coap import coap
from coap import coapDefines as d

CONFIG_FILENAME = 'rstorm.config'
DFLT_IPv6       = 'bbbb::'
DFLT_PERIOD     = 10

class RStormGUI(object):

    def __init__(self, master):
        
        (ipv6,period) = self._readConfigFile()
        
        self.master = master
        self.ipv6_addr = StringVar()
        self.ipv6_addr.set(ipv6)
        self.period = IntVar()
        self.period.set(period)
        self.status = StringVar()
        self.status.set('')
        self.coap = coap.coap()
        self.create_gui()
        self.master.mainloop()

    def create_gui(self):
        self.master.wm_title("rstorm client")

        f = Frame(self.master,padx=5,pady=5)
        Label(f,text="IETF90 plugfest - CoAP rstorm client for OpenWSN").pack(side=LEFT,expand=NO)
        f.pack(side=TOP,expand=YES,fill=X)

        f = Frame(self.master,height=2,bd=1,relief=SUNKEN,padx=5,pady=5)
        f.pack(side=TOP,fill=X)
        
        f = Frame(self.master,padx=5,pady=5)
        Label(f,text="coap://[").pack(side=LEFT,expand=NO)
        Entry(f,textvariable=self.ipv6_addr,width=40).pack(side=LEFT,expand=YES,fill=X)
        Label(f,text="]/storm period=").pack(side=LEFT,expand=NO)
        Entry(f,textvariable=self.period,width=10).pack(side=LEFT,expand=NO)
        f.pack(side=TOP,expand=YES,fill=X)
        
        f = Frame(self.master,height=2,bd=1,relief=SUNKEN,padx=5,pady=5)
        f.pack(side=TOP,fill=X)
        
        f = Frame(self.master,padx=5,pady=5)
        Button(f,text="GET",width=10,command=self.get_cmd,default=ACTIVE).pack(side=RIGHT,expand=NO)
        Button(f,text="PUT",width=10,command=self.put_cmd,default=ACTIVE).pack(side=RIGHT,expand=NO)
        Label(f,textvariable=self.status,anchor=W).pack(side=LEFT,expand=YES,fill=X)
        f.pack(side=TOP,expand=YES,fill=X)

        self.master.protocol("WM_DELETE_WINDOW", self.close)
        
    def validate(self,check_period=True):
        if check_period:
            try:
                per = self.period.get()
            except:
                tkMessageBox.showwarning("Period","Invalid number for period")
                return False
            
            if (per < 0) or (per > (2**16-1)):
                tkMessageBox.showwarning("Period","Invalid range for period [0-65535]")
                return False
        
        ipv6 = self.ipv6_addr.get().strip()
        self.ipv6_addr.set(ipv6)
        
        # http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
        pattern = r"\b(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|" + \
            r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|" + \
            r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|" + \
            r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|" + \
            r":((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|" + \
            r"::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|" + \
            r"(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|" + \
            r"1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\b"
        
        if re.match(pattern, ipv6):
            return True
        else:
            tkMessageBox.showwarning("IPv6","Invalid IPv6 address")
            return False
            
        return True

    def get_cmd(self, event=None):
        self._writeConfigFile()
        if self.validate(False):
            self.status.set('')
            self.master.update_idletasks()
            ipv6 = self.ipv6_addr.get().strip()
            per = self.period.get()
            uri = 'coap://[{0}]/strm/period'.format(ipv6)
            self.status.set(uri)
            try:
                r = self.coap.GET(uri)
                per = struct.unpack('>H',''.join([ chr(c) for c in r ]))[0]
            except Exception, e:
                self.status.set('Failed: {0}'.format(repr(e)))
            else:
                self.period.set(per)
                self.status.set('GET OK!')

    def put_cmd(self, event=None):
        self._writeConfigFile()
        if self.validate():
            self.status.set('')
            self.master.update_idletasks()
            ipv6 = self.ipv6_addr.get().strip()
            uri = 'coap://[{0}]/strm/period'.format(ipv6)
            per = self.period.get()
            per = [ ord(c) for c in struct.pack('>H',per) ]
            self.status.set(uri)
            try:
                r = self.coap.PUT(uri,payload=per)
            except Exception, e:
                self.status.set('Failed: {0}'.format(repr(e)))
            else:
                self.status.set('PUT OK!')
        
    def close(self):
        if self.coap:
            self.coap.close()
        self.master.destroy()
    
    def _writeConfigFile(self):
        
        output  = []
        output += ['ipv6={0}'.format(self.ipv6_addr.get().strip())]
        output += ['period={0}'.format(self.period.get())]
        output  = '\n'.join(output)
        
        with open(CONFIG_FILENAME,'w') as f:
            f.write(output)
    
    def _readConfigFile(self):
        
        ipv6   = DFLT_IPv6
        period = DFLT_PERIOD
        
        try:
            with open(CONFIG_FILENAME,'r') as f:
                for line in f:
                    m = re.search('ipv6=(\S+)', line)
                    if m:
                        ipv6 = m.group(1).strip()
                    m = re.search('period=([0-9]+)', line)
                    if m:
                        period = m.group(1).strip()
        except Exception as err:
            pass
        
        return (ipv6,period)

def main():
    RStormGUI(Tk())

if __name__=="__main__":
    main()