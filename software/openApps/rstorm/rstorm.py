import os
import sys
from Tkinter import *
import tkMessageBox
import re
import time
import struct
import threading

p = os.path.dirname(sys.argv[0])
p = os.path.join(p,'..','..','..','..','coap')
p = os.path.abspath(p)
sys.path.insert(0,p)

from coap import coap
from coap import coapDefines as d

CONFIG_FILENAME = 'rstorm.config'
DFLT_IPv6       = 'bbbb::'
DFLT_PERIOD     = 10
GUI_REFRESH_MS  = 500

class ThreadDeferrer(threading.Thread):
    def __init__(self,cmd,args=[],kwargs={},cb_ok=None,cb_fail=None):
        self.cmd                  = cmd
        self.args                 = args
        self.kwargs               = kwargs
        self.cb_ok                = cb_ok
        self.cb_fail              = cb_fail
        threading.Thread.__init__(self)
        self.start()
    def run(self):
        try:
            response              = self.cmd(*self.args,**self.kwargs)
        except Exception as err:
            if self.cb_fail:
                self.cb_fail(err)
        else:
            if self.cb_ok:
                self.cb_ok(response)

class CoapHandler(object):
    
    def __init__(self):
        self.dataLock             = threading.RLock()
        self.coap                 = coap.coap()
        self.busy                 = False
        self.statusBusy           = False
        self._status              = ''
        self.statusStart          = None
        self.period               = None
    
    #===== retrieve period
    
    def retrieve(self,uri):
        with self.dataLock:
            if self.busy:
                self.statusBusy   = True
                return
            self.busy             = True
            self.statusBusy       = False
            self.status           = 'GET {0}'.format(uri)
            self.statusStart      = time.time()
        ThreadDeferrer(
            cmd                   = self.coap.GET,
            args                  = [uri],
            kwargs                = {},
            cb_ok                 = self.retrieve_cb_ok,
            cb_fail               = self.retrieve_cb_fail,
        )
    
    def retrieve_cb_ok(self,response):
        try:
            period = struct.unpack('>H',''.join([chr(c) for c in response]))[0]
        except Exception as err:
            with self.dataLock:
                self.status       = 'Failed: {0}'.format(err)
        else:
            with self.dataLock:
                self.status       = 'GET OK!'
                self.period       = period
        finally:
            with self.dataLock:
                self.busy         = False
                self.statusBusy   = False
                self.statusStart  = None
    
    def retrieve_cb_fail(self,err):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'GET Failed: {0}'.format(err)
            self.statusStart      = None
    
    #===== update period
    
    def update_period(self,uri,period):
        with self.dataLock:
            if self.busy:
                self.statusBusy   = True
                return
            self.busy             = True
            self.statusBusy       = False
            self.status           = 'PUT {0} period={1}'.format(uri,period)
            self.statusStart      = time.time()
        ThreadDeferrer(
            cmd                   = self.coap.PUT,
            args                  = [uri],
            kwargs                = {'payload': period},
            cb_ok                 = self.update_cb_ok,
            cb_fail               = self.update_cb_fail,
        )
    
    def update_cb_ok(self,response):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'PUT OK!'
            self.statusStart      = None
    
    def update_cb_fail(self,err):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'PUT Failed: {0}'.format(err)
            self.statusStart      = None
    
    #===== getters
    
    def getStatus(self):
        with self.dataLock:
            returnVal  = []
            if self.statusBusy:
                returnVal += ['[busy] '.format(time.time()-self.statusStart)]
            returnVal += [self.status]
            if self.statusStart!=None:
                returnVal += [' ({0}s)'.format(int(time.time()-self.statusStart))]
        returnVal = ''.join(returnVal)
        return returnVal
    
    def getPeriod(self):
        with self.dataLock:
            returnVal = self.period
            self.period = None
        return returnVal
    
    #===== getters
    
    @property
    def status(self):
        with self.dataLock:
            return self._status
    
    @status.setter
    def status(self,value):
        print value
        with self.dataLock:
            self._status = value
    
    #===== admin
    
    def close(self):
        self.coap.close()

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
        self.coapHandler = CoapHandler()
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
        self.guiPeriod = Entry(f,textvariable=self.period,width=10)
        self.guiPeriod.pack(side=LEFT,expand=NO)
        self.guiPeriod.after(GUI_REFRESH_MS,self.updatePeriod)
        f.pack(side=TOP,expand=YES,fill=X)
        
        f = Frame(self.master,height=2,bd=1,relief=SUNKEN,padx=5,pady=5)
        f.pack(side=TOP,fill=X)
        
        f = Frame(self.master,padx=5,pady=5)
        Button(f,text="GET",width=10,command=self.get_cmd,default=ACTIVE).pack(side=RIGHT,expand=NO)
        Button(f,text="PUT",width=10,command=self.put_cmd,default=ACTIVE).pack(side=RIGHT,expand=NO)
        self.guiStatus = Label(f,textvariable=self.status,anchor=W)
        self.guiStatus.pack(side=LEFT,expand=YES,fill=X)
        self.guiStatus.after(GUI_REFRESH_MS,self.updateStatus)
        f.pack(side=TOP,expand=YES,fill=X)

        self.master.protocol("WM_DELETE_WINDOW", self.close)
    
    def updatePeriod(self):
        newPeriod = self.coapHandler.getPeriod()
        if newPeriod!=None:
            self.period.set(newPeriod)
        self.guiPeriod.after(GUI_REFRESH_MS,self.updatePeriod)
    
    def updateStatus(self):
        newStatus = self.coapHandler.getStatus()
        self.status.set(newStatus)
        self.guiStatus.after(GUI_REFRESH_MS,self.updateStatus)
    
    def validate(self,check_period=True):
        if check_period:
            try:
                period = self.period.get()
            except:
                tkMessageBox.showwarning("Period","Invalid number for period")
                return False
            
            if (period < 0) or (period > (2**16-1)):
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
        if self.validate(False):
            self.master.update_idletasks()
            ipv6   = self.ipv6_addr.get().strip()
            uri    = 'coap://[{0}]/storm'.format(ipv6)
            self.coapHandler.retrieve(uri)
        self._writeConfigFile()

    def put_cmd(self, event=None):
        self._writeConfigFile()
        if self.validate():
            self.status.set('')
            self.master.update_idletasks()
            ipv6   = self.ipv6_addr.get().strip()
            uri    = 'coap://[{0}]/storm/'.format(ipv6)
            period = self.period.get()
            period = [ ord(c) for c in struct.pack('>H',period) ]
            self.coapHandler.update_period(uri,period)

    def close(self):
        self.coapHandler.close()
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
