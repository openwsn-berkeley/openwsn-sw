#!/usr/bin/python

import string
import numpy as np
import matplotlib.pyplot as plt
import os

# ============== define ===================

# =============== structure ===============
slotframe = []
numOfCell = []
packetInQueue = []
sentPacket = []
traffic = []        
# =============== prototype ===============

output = open('output.txt','r')
line = output.readline()
while line != '':
    if line[0]>='0' and line[0]<='9':
        data = line.split(',')
        slotframe.append(int(data[0]))
        numOfCell.append(int(data[1]))
        packetInQueue.append(int(data[2]))
        sentPacket.append(int(data[2]))
        traffic.append(int(data[2]))
    line = output.readline()
output.close()
        
x_slotframe = np.int_(slotframe)
y_numOfCell = np.int_(numOfCell)
y_packetInQueue = np.int_(packetInQueue) 
y_sentPacket = np.int_(sentPacket)
y_traffic = np.int_(traffic)

z1 = np.polyfit(x_slotframe,y_numOfCell,12)
z2 = np.polyfit(x_slotframe,y_packetInQueue,12)
z3 = np.polyfit(x_slotframe,y_sentPacket,12)
z4 = np.polyfit(x_slotframe,y_traffic,12)

fit1 = np.poly1d(z1)
fit2 = np.poly1d(z2)
fit3 = np.poly1d(z3)
fit4 = np.poly1d(z4)

y_new1 = fit1(x_slotframe)
y_new2 = fit2(x_slotframe)
y_new3 = fit3(x_slotframe)
y_new4 = fit4(x_slotframe)

#================ raw data ====================
plt.plot(x_slotframe,y_numOfCell,label='numOfCell')
plt.plot(x_slotframe,y_packetInQueue,label='packetInQueue')
plt.plot(x_slotframe,y_sentPacket,label='sentPacket')
plt.plot(x_slotframe,y_traffic,label='traffic')

#================  curve fitting ==============
# plt.plot(x_slotframe,y_new1,label='numOfCell')
# plt.plot(x_slotframe,y_new2,label='packetInQueue')
# plt.plot(x_slotframe,y_new3,label='sentPacket')
# plt.plot(x_slotframe,y_new4,label='traffic')

legend = plt.legend(shadow=True, fontsize='x-large')

plt.xlim(slotframe[0], slotframe[-1])
plt.xlabel('slotframe')
plt.title('pid test (kp:1,ki:0.002,kd:-0.01)')

plt.show()
