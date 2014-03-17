import threading

class VcdLogger(object):
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    SIGNAMES  = ['frame','slot','fsm','task','isr','radio']
    
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
        self.f          = open('debugpins.vcd','w')
        self.signame    = {}
        self.lastTs     = 0
        self.dataLock   = threading.Lock()
        sigChar         = ord('!')
        
        # create header
        header  = []
        header += ['$timescale 1ns $end\n']
        header += ['$scope module logic $end\n']
        for mote in [1,2]: # poipoi
            for signal in self.SIGNAMES:
                self.signame[(mote,signal)] = chr(sigChar)
                header += [
                    '$var wire 1 {0} {1}_{2} $end\n'.format(
                        chr(sigChar),
                        mote,
                        signal,
                    )
                ]
                sigChar += 1
        header += ['$upscope $end\n']
        header += ['$enddefinitions $end\n']
        header += ['#0\n']
        for ((mote,signal),sigChar) in self.signame.items():
            header += ['0{0}\n'.format(self.signame[(mote,signal)])]
        header  = ''.join(header)
        
        # write header
        self.f.write(header)
    
    def log(self,ts,mote,signal,state):
        
        assert signal in self.SIGNAMES
        assert state in [True,False]
        
        if signal in ['isr','task']:
            return # poipoi
        
        # cofig state to val
        if state:
            val = 1
        else:
            val = 0
        
        with self.dataLock:
            # format
            output  = []
            if ts!=self.lastTs:
                #output += ['#{0}\n'.format(int((ts-self.lastTs)*1000000000))]
                output += ['#{0}\n'.format(int(ts*1000000)*1000)]
            output += ['{0}{1}\n'.format(val,self.signame[(mote,signal)])]
            output  = ''.join(output)
            
            # write
            self.f.write(output)
            
            # remember ts
            self.lastTs = ts
        