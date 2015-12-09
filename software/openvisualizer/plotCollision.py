#!/usr/bin/python

import string
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# == define

SLOT_FRAME = 101
width      = 0.1

NUMOFCHAN  = 16
NUMOFCELLS = 9

class fileProcess(object):
    def __init__(self,dagroot,mote1,mote2):
        self.dagroot    = dagroot
        self.mote1      = mote1
        self.mote2      = mote2
        self.receivedFromMote1 = [[0 for m in range(NUMOFCHAN)] for i in range(NUMOFCELLS)]
        self.receivedFromMote2 = [[0 for m in range(NUMOFCHAN)] for i in range(NUMOFCELLS)]
        self.sentByMote1 = [[0 for m in range(NUMOFCHAN)] for i in range(NUMOFCELLS)]
        self.sentByMote2 = [[0 for m in range(NUMOFCHAN)] for i in range(NUMOFCELLS)]
        self.pdrMote1    = [[0 for m in range(NUMOFCHAN)] for i in range(NUMOFCELLS)]
        self.pdrMote2    = [[0 for m in range(NUMOFCHAN)] for i in range(NUMOFCELLS)]
    
    def getPdr(self):
        # collect packet received by dagroot  
        file = open(self.dagroot,'r')
        for line in file:
            temp    = line[1:-2].split(',')
            if len(temp) == 12:
                slot = int(temp[6])+256*int(temp[7])
                chan = int(temp[8])-11
                if hex(int(temp[-2]))=='0x99':
                    self.receivedFromMote1[slot][chan] += 1
                elif hex(int(temp[-2]))=='0xa3':
                    self.receivedFromMote1[slot][chan] += 1
        file.close()
        
        # collect packet sent by mote1
        file = open(self.mote1,'r')
        for line in file:
            temp    = line[1:-2].split(',')
            if len(temp) == 12:
                slot = int(temp[6])+256*int(temp[7])
                chan = int(temp[8])-11
                if hex(int(temp[-2]))=='0x99':
                    self.sentByMote1[slot][chan] += 1
        file.close()
        
        # collect packet sent by mote2
        file = open(self.mote2,'r')
        for line in file:
            temp    = line[1:-2].split(',')
            if len(temp) == 12:
                slot = int(temp[6])+256*int(temp[7])
                chan = int(temp[8])-11
                if hex(int(temp[-2]))=='0xa3':
                    self.sentByMote1[slot][chan] += 1
        file.close()
        
        # calculate PDR
        for i in range(NUMOFCELLS):
            for j in range(NUMOFCHAN):
                if self.sentByMote1[i][j] != 0:
                    self.pdrMote1[i][j] = float(self.receivedFromMote1[i][j])/float(self.sentByMote1[i][j])
                else:   
                    self.pdrMote1[i][j] = 0
                if self.sentByMote2[i][j] != 0:
                    self.pdrMote2[i][j] = float(self.receivedFromMote2[i][j])/float(self.sentByMote2[i][j])
                else:
                    self.sentByMote2[i][j] = 0
        
    def plotPdr(self):
        # calculate the pdr on each channel
        channelPDR = np.transpose(self.pdrMote1)
        cmaps = ['aqua', 'black',    'blue',    'blueviolet', 
                 'brown','chartreuse',   'coral', 'cornflowerblue', 
                 'forestgreen',  'darkslateblue',  'darkred',    'firebrick', 
                 'forestgreen',  'gold',    'gray',    'lawngreen']
        style = ['.',',','o','v','^','<','>','_','|','d','D','s','p','*','h','H']
        
                 
        xs = np.float_([i for i in range(NUMOFCELLS)])
        scatterFig = plt.figure()
        ax = plt.subplot(111)
        for i in range(NUMOFCHAN):
            ax.plot(xs,channelPDR[i],style[i]+'-',color=cmaps[i],label='ch '+str(i+11))
        ax.grid(True)
        # ax.set_title('PDR per channel on each slot (distance = {0}m)'.format(str(int(TxFile[-7:-4])/100.0)))
        ax.set_xlabel('slotoffset')
        ax.set_ylabel('packet delivery rate')
        ax.set_xlim(0.1,8.05)
        ax.set_ylim(-0.1,1.05)
        
        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        scatterFig.show()
        
def main():
    file1  = fileProcess('collision@m3-205.txt','collision@m3-206.txt','collision@m3-207.txt')
    file1.getPdr()
    file1.plotPdr()
    raw_input()
    
def animation_main():
    global line
    file  = fileProcess('collision@m3-205.txt')
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
    # animation_main()
    main()