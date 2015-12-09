#!/usr/bin/python

import string
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# == define

SLOT_FRAME = 101
width      = 0.1

class fileProcess(object):
    def __init__(self,data):
        self.data       = data
        self.pdr        = [0 for i in range(SLOT_FRAME)]
        self.sentPacket = [0 for i in range(SLOT_FRAME)]
        self.id         = None 
        self.lastLine   = None 
    
    def getPdr(self):
        file = open(self.data,'r')
        for line in file:
            temp    = line[1:-2].split(',')
            length  = int(temp[0])
            self.id = hex(int(temp[1]))
            for i in range(len(temp[2:])/3):
                if int(temp[2+i*3+2]) == 0:
                    self.pdr[int(temp[2+i*3])] = 0
                else:
                    self.pdr[int(temp[2+i*3])] = float(temp[2+i*3+2])/float(temp[2+i*3+1])
                yield self.pdr
        
        file.close()
        
def main():
    file1  = fileProcess('moteProbe@m3-205.txt')
    file1.getPdr()
    file2  = fileProcess('moteProbe@m3-206.txt')
    file2.getPdr()
    file3  = fileProcess('moteProbe@m3-207.txt')
    file3.getPdr()
    file4  = fileProcess('moteProbe@m3-208.txt')
    file4.getPdr()
    file5  = fileProcess('moteProbe@m3-209.txt')
    file5.getPdr()
    file6  = fileProcess('moteProbe@m3-210.txt')
    file6.getPdr()   
    file7  = fileProcess('moteProbe@m3-211.txt')
    file7.getPdr()    
    
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file1.pdr),label=file1.id)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file2.pdr),label=file2.id)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file3.pdr),label=file3.id)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file4.pdr),label=file4.id)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file5.pdr),label=file5.id)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file6.pdr),label=file6.id)
    ax.plot(np.int_([i for i in range(SLOT_FRAME)]),np.float_(file7.pdr),label=file7.id)
    ax.set_ylim([0,1.05])
    ax.grid(True)
    ax.legend()
    fig.show()
    raw_input("Enter to quit\n") 
    
def animation_main():
    global line
    file  = fileProcess('moteProbe@m3-210.txt')
    fig, ax = plt.subplots()
    line, = ax.plot(np.int_([0 for i in range(SLOT_FRAME)]))
    ax.set_ylim(0, 1.05)
    ani = animation.FuncAnimation(fig, update, file.getPdr, init_func=init, interval=100)
    plt.show()
    
def init():
    line.set_ydata(np.int_([0 for i in range(SLOT_FRAME)]))
    return line,
    
def update(data):
    line.set_ydata(data)
    return line,
    
if __name__=='__main__':
    animation_main()
    # main()