import os
import traceback
import threading

class VcdLogger(object):
    
    ACTIVITY_DUR   = 1000 # 1000ns=1us
    FILENAME       = 'debugpins.vcd'
    FILENAME_SWAP  = 'debugpins.vcd.swap'
    ENDVAR_LINE    = '$upscope $end\n'
    ENDDEF_LINE    = '$enddefinitions $end\n'
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    SIGNAMES  = ['frame','slot','fsm','task','isr','radio','ka','syncPacket','syncAck','debug']
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VcdLogger, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    #======================== main ============================================
    
    def __init__(self):
        
        # don't re-initialize an instance (singleton pattern)
        if self._init:
            return
        self._init = True
        
        # local variables
        self.f          = open(self.FILENAME,'w')
        self.signame    = {}
        self.lastTs     = {}
        self.dataLock   = threading.RLock()
        self.enabled    = False
        self.sigChar    = ord('!')
        
        # create header
        header          = []
        header         += ['$timescale 1ns $end\n']
        header         += ['$scope module logic $end\n']
        # variables will be declared here by self._addMote()
        header         += [self.ENDVAR_LINE]
        header         += [self.ENDDEF_LINE]
        header          = ''.join(header)
        
        # write header
        self.f.write(header)
    
    #======================== public ==========================================
    
    def setEnabled(self,enabled):
        assert enabled in [True,False]
        
        with self.dataLock:
            self.enabled = enabled
    
    def log(self,ts,mote,signal,state):
        
        assert signal in self.SIGNAMES
        assert state in [True,False]
        
        # stop here if not enables
        with self.dataLock:
            if not self.enabled:
                return
        
        # translate state to val
        if state:
            val = 1
        else:
            val = 0
        
        with self.dataLock:
            
            # add mote if needed
            if mote not in self.signame:
                self._addMote(mote)
            
            # format
            output  = []
            tsTemp = int(ts*1000000)*1000
            if ((mote,signal) in self.lastTs) and self.lastTs[(mote,signal)]==ts:
                tsTemp += self.ACTIVITY_DUR
            output += ['#{0}\n'.format(tsTemp)]
            output += ['{0}{1}\n'.format(val,self.signame[mote][signal])]
            output  = ''.join(output)
            
            # write
            self.f.write(output)
            
            # remember ts
            self.lastTs[(mote,signal)] = ts
    
    #======================== private =========================================
    
    def _addMote(self,mote):
        assert mote not in self.signame
        
        #=== populate signame
        self.signame[mote] = {}
        for signal in self.SIGNAMES:
            self.signame[mote][signal] = chr(self.sigChar)
            self.sigChar += 1
        
        #=== close FILENAME
        self.f.close()
        
        #=== FILENAME -> FILENAME_SWAP
        fswap = open(self.FILENAME_SWAP,'w')
        for line in open(self.FILENAME,'r'):
            # declare variables
            if line==self.ENDVAR_LINE:
                for signal in self.SIGNAMES:
                    fswap.write(
                        '$var wire 1 {0} {1}_{2} $end\n'.format(
                            self.signame[mote][signal],
                            mote,
                            signal,
                        )
                    )
            # print line
            fswap.write(line)
            # initialize variables
            if line==self.ENDDEF_LINE:
                for signal in self.SIGNAMES:
                    fswap.write('#0\n')
                    fswap.write('0{0}\n'.format(self.signame[mote][signal]))
        fswap.close()
        
        #=== FILENAME_SWAP -> FILENAME
        os.remove(self.FILENAME)
        os.rename(self.FILENAME_SWAP, self.FILENAME)
        
        #=== re-open FILENAME
        self.f = open(self.FILENAME,'a')
