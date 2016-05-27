import os
import sys
import Tkinter
import tkMessageBox
import re
import time
import struct
import threading

if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..','..','..','..','coap'))

from coap import coap
from coap import coapDefines as d

CONFIG_FILENAME = '{0}.config'.format(os.path.basename(__file__).split('.')[0])
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

class IETF90Client(object):
    
    #=== singleton pattern start ===
    _instance = None
    _init     = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IETF90Client, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    #=== singleton pattern stop ===
    
    def __init__(self):
        
        #=== singleton pattern start ===
        if self._init:
            return
        self._init = True
        #=== singleton pattern stop ===
        
        # local variables
        self.dataLock             = threading.RLock()
        self.coap                 = coap.coap()
        self.busy                 = False
        self.statusBusy           = False
        self._status              = ''
        self.statusStart          = None
        self.period               = None
    
    #===== getStormPeriod
    
    def getStormPeriod(self,ipv6):
        with self.dataLock:
            if self.busy:
                self.statusBusy   = True
                return
        
        uri                       = 'coap://[{0}]/storm'.format(ipv6)
        with self.dataLock:
            self.busy             = True
            self.statusBusy       = False
            self.status           = 'GET {0}'.format(uri)
            self.statusStart      = time.time()
        
        ThreadDeferrer(
            cmd                   = self.coap.GET,
            args                  = [uri],
            kwargs                = {},
            cb_ok                 = self.getStormPeriod_cb_ok,
            cb_fail               = self.getStormPeriod_cb_fail,
        )
    
    def getStormPeriod_cb_ok(self,response):
        try:
            period                = struct.unpack('>H',''.join([chr(c) for c in response]))[0]
        except Exception as err:
            with self.dataLock:
                self.status       = 'Failed: {0}'.format(err)
        else:
            with self.dataLock:
                self.status       = 'GET success'
                self.period       = period
        finally:
            with self.dataLock:
                self.busy         = False
                self.statusBusy   = False
                self.statusStart  = None
    
    def getStormPeriod_cb_fail(self,err):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'GET failed: {0}'.format(err)
            self.statusStart      = None
    
    #===== setStormPeriod
    
    def setStormPeriod(self,ipv6,period):
        with self.dataLock:
            if self.busy:
                self.statusBusy   = True
                return
        
        uri                       = 'coap://[{0}]/storm'.format(ipv6)
        
        with self.dataLock:
            self.busy             = True
            self.statusBusy       = False
            self.status           = 'PUT {0} period={1}'.format(uri,period)
            self.statusStart      = time.time()
        ThreadDeferrer(
            cmd                   = self.coap.PUT,
            args                  = [uri],
            kwargs                = {'payload': [ ord(c) for c in struct.pack('>H',period) ]},
            cb_ok                 = self.setStormPeriod_cb_ok,
            cb_fail               = self.setStormPeriod_cb_fail,
        )
    
    def setStormPeriod_cb_ok(self,response):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'PUT success'
            self.statusStart      = None
    
    def setStormPeriod_cb_fail(self,err):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'PUT failed: {0}'.format(err)
            self.statusStart      = None
    
    #===== add6topCell
    
    def add6topCell(self,ipv6):
        with self.dataLock:
            if self.busy:
                self.statusBusy   = True
                return
        
        uri                       = 'coap://[{0}]/6t'.format(ipv6)
        with self.dataLock:
            self.busy             = True
            self.statusBusy       = False
            self.status           = 'PUT {0}'.format(uri)
            self.statusStart      = time.time()
        
        ThreadDeferrer(
            cmd                   = self.coap.PUT,
            args                  = [uri],
            kwargs                = {},
            cb_ok                 = self.add6topCell_cb_ok,
            cb_fail               = self.add6topCell_cb_fail,
        )
    
    def add6topCell_cb_ok(self,response):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'PUT success'
            self.statusStart      = None
    
    def add6topCell_cb_fail(self,err):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'PUT failed: {0}'.format(err)
            self.statusStart      = None
    
    #===== delete6topCell
    
    def delete6topCell(self,ipv6):
        with self.dataLock:
            if self.busy:
                self.statusBusy   = True
                return
        
        uri                       = 'coap://[{0}]/6t'.format(ipv6)
        with self.dataLock:
            self.busy             = True
            self.statusBusy       = False
            self.status           = 'DELETE {0}'.format(uri)
            self.statusStart      = time.time()
        
        ThreadDeferrer(
            cmd                   = self.coap.DELETE,
            args                  = [uri],
            kwargs                = {},
            cb_ok                 = self.delete6topCell_cb_ok,
            cb_fail               = self.delete6topCell_cb_fail,
        )
    
    def delete6topCell_cb_ok(self,response):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'DELETE success'
            self.statusStart      = None
    
    def delete6topCell_cb_fail(self,err):
        with self.dataLock:
            self.busy             = False
            self.statusBusy       = False
            self.status           = 'DELETE failed: {0}'.format(err)
            self.statusStart      = None
    
    #===== getters
    
    def getStatus(self):
        with self.dataLock:
            returnVal  = []
            if self.statusBusy:
                returnVal += ['[busy] ']
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
            self._status     = value
    
    #===== admin
    
    def close(self):
        self.coap.close()
        self._instance       = None
        self._init           = False

class IETF90ClientGUI(object):

    def __init__(self):
        
        #=== read configuration from file
        (ipv6,period)        = self._readConfigFile()
        
        #=== local variable
        self.guiroot         = Tkinter.Tk()
        self.guiroot.resizable(False,False)
        self.ipv6_addr       = Tkinter.StringVar()
        self.ipv6_addr.set(ipv6)
        self.period          = Tkinter.IntVar()
        self.period.set(period)
        self.status          = Tkinter.StringVar()
        self.status.set('')
        
        #=== create GUI interface
        
        # close button
        self.guiroot.protocol("WM_DELETE_WINDOW", self._cb_close)
        
        # title
        self.guiroot.wm_title("IETF90 CoAP client - OpenWSN")
        
        # row: ipv6
        f = Tkinter.Frame(self.guiroot,padx=5,pady=5)
        Tkinter.Label(f,text="coap://[").pack(side=Tkinter.LEFT,expand=Tkinter.NO)
        Tkinter.Entry(f,textvariable=self.ipv6_addr,width=40).pack(side=Tkinter.LEFT,expand=Tkinter.YES,fill=Tkinter.X)
        Tkinter.Label(f,text="]/").pack(side=Tkinter.LEFT,expand=Tkinter.NO)
        f.pack(side=Tkinter.TOP,expand=Tkinter.YES,fill=Tkinter.X)
        
        # row: separator
        f = Tkinter.Frame(self.guiroot,height=2,bd=1,relief=Tkinter.SUNKEN,padx=5,pady=5)
        f.pack(side=Tkinter.TOP,fill=Tkinter.X)
        
        # row: /storm
        f = Tkinter.Frame(self.guiroot,padx=5,pady=5)
        Tkinter.Label(f,text="/storm period=").pack(side=Tkinter.LEFT,expand=Tkinter.NO)
        self.guiPeriod = Tkinter.Entry(f,textvariable=self.period,width=10)
        self.guiPeriod.pack(side=Tkinter.LEFT,expand=Tkinter.NO)
        self.guiPeriod.after(GUI_REFRESH_MS,self._refresh_period)
        Tkinter.Button(f,text="PUT",width=10,command=self._cb_storm_PUT,default=Tkinter.ACTIVE).pack(side=Tkinter.RIGHT,expand=Tkinter.NO)
        Tkinter.Button(f,text="GET",width=10,command=self._cb_storm_GET,default=Tkinter.ACTIVE).pack(side=Tkinter.RIGHT,expand=Tkinter.NO)
        f.pack(side=Tkinter.TOP,expand=Tkinter.YES,fill=Tkinter.X)
        
        # row: separator
        f = Tkinter.Frame(self.guiroot,height=2,bd=1,relief=Tkinter.SUNKEN,padx=5,pady=5)
        f.pack(side=Tkinter.TOP,fill=Tkinter.X)
        
        # row: /6t
        f = Tkinter.Frame(self.guiroot,padx=5,pady=5)
        Tkinter.Label(f,text="/6t").pack(side=Tkinter.LEFT,expand=Tkinter.NO)
        Tkinter.Button(f,text="DELETE",width=10,command=self._cb_6t_DELETE,default=Tkinter.ACTIVE).pack(side=Tkinter.RIGHT,expand=Tkinter.NO)
        Tkinter.Button(f,text="PUT",width=10,command=self._cb_6t_PUT,default=Tkinter.ACTIVE).pack(side=Tkinter.RIGHT,expand=Tkinter.NO)
        f.pack(side=Tkinter.TOP,expand=Tkinter.YES,fill=Tkinter.X)
        
        # row: separator
        f = Tkinter.Frame(self.guiroot,height=2,bd=1,relief=Tkinter.SUNKEN,padx=5,pady=5)
        f.pack(side=Tkinter.TOP,fill=Tkinter.X)
        
        # row: status
        f = Tkinter.Frame(self.guiroot,padx=5,pady=5)
        self.guiStatus = Tkinter.Label(f,textvariable=self.status,anchor=Tkinter.W)
        self.guiStatus.pack(side=Tkinter.LEFT,expand=Tkinter.YES,fill=Tkinter.X)
        self.guiStatus.after(GUI_REFRESH_MS,self._refresh_status)
        f.pack(side=Tkinter.TOP,expand=Tkinter.YES,fill=Tkinter.X)
        
        #=== start GUI
        self.guiroot.mainloop()
    
    #======================== GUI refreshers ==================================
    
    def _refresh_period(self):
        newPeriod = IETF90Client().getPeriod()
        if newPeriod!=None:
            self.period.set(newPeriod)
        self.guiPeriod.after(GUI_REFRESH_MS,self._refresh_period)
    
    def _refresh_status(self):
        newStatus = IETF90Client().getStatus()
        self.status.set(newStatus)
        self.guiStatus.after(GUI_REFRESH_MS,self._refresh_status)
    
    #======================== GUI helpers =====================================
    
    def _get_ipv6_entry(self):
        ipv6 = self.ipv6_addr.get().strip()
        self.ipv6_addr.set(ipv6)
        return ipv6
    
    #======================== GUI callbacks ===================================
    
    def _cb_close(self):
        IETF90Client().close()
        self.guiroot.destroy()
    
    def _cb_storm_GET(self, event=None):
        try:
            self._validate_entry_ipv6()
        except ValueError as err:
            tkMessageBox.showwarning('Oops!',str(err))
            return
        
        ipv6   = self._get_ipv6_entry()
        IETF90Client().getStormPeriod(ipv6)
        
        self._writeConfigFile()
    
    def _cb_storm_PUT(self, event=None):
        try:
            self._validate_entry_ipv6()
            self._validate_entry_period()
        except ValueError as err:
            tkMessageBox.showwarning('Oops!',str(err))
            return
        
        ipv6   = self._get_ipv6_entry()
        period = self.period.get()
        IETF90Client().setStormPeriod(ipv6,period)
        
        self._writeConfigFile()
    
    def _cb_6t_PUT(self, event=None):
        try:
            self._validate_entry_ipv6()
        except ValueError as err:
            tkMessageBox.showwarning('Oops!',str(err))
            return
        
        ipv6   = self._get_ipv6_entry()
        IETF90Client().add6topCell(ipv6)
        
        self._writeConfigFile()
    
    def _cb_6t_DELETE(self, event=None):
        try:
            self._validate_entry_ipv6()
        except ValueError as err:
            tkMessageBox.showwarning('Oops!',str(err))
            return
        
        ipv6   = self._get_ipv6_entry()
        IETF90Client().delete6topCell(ipv6)
        
        self._writeConfigFile()
    
    #======================== format validation ===============================
    
    def _validate_entry_ipv6(self):
        
        # http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
        IPv6_PATTERN = r"\b(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|" + \
            r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|" + \
            r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|" + \
            r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|" + \
            r":((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|" + \
            r"::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|" + \
            r"(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|" + \
            r"1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\b"
        
        ipv6 = self._get_ipv6_entry()
        
        if not re.match(IPv6_PATTERN, ipv6):
            raise ValueError("Invalid IPv6 address")
    
    def _validate_entry_period(self):
        try:
            period = self.period.get()
        except:
            raise ValueError("Invalid number for period")
        
        if (period<0x0000) or (period>0xffff):
            raise ValueError("Invalid range for period [0x0000-0xffff]")
    
    #======================== file interaction ================================
    
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
        
        return ipv6, period

def main():
    IETF90Client()
    IETF90ClientGUI()

if __name__=="__main__":
    main()
