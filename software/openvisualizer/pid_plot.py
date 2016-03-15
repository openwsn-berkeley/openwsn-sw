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
error   = []

    
# =============== prototype ===============

output = open('output.txt','r')
line = output.readline()
while line != '':
    if '0' <= line[0] <= '9':
        data = line.split(',')
        try:
            slotframe.append(int(data[0]))
            numOfCell.append(int(data[1]))
            packetInQueue.append(int(data[2]))
            sentPacket.append(int(data[3]))
            traffic.append(1515/int(data[4]))
            error.append(int(data[5]))
        except ValueError as err:
            print err
    line = output.readline()
output.close()

slotframe = [i-slotframe[0] for i in slotframe]
        
x_slotframe = np.int_(slotframe)
y_numOfCell = np.int_(numOfCell)
y_packetInQueue = np.int_(packetInQueue) 
y_sentPacket = np.int_(sentPacket)
y_traffic = np.int_(traffic)
y_error = np.int_(error)

z1 = np.polyfit(x_slotframe,y_numOfCell,15)
z2 = np.polyfit(x_slotframe,y_packetInQueue,15)
z3 = np.polyfit(x_slotframe,y_sentPacket,15)
z4 = np.polyfit(x_slotframe,y_traffic,15)
z5 = np.polyfit(x_slotframe,y_error,15)

fit1 = np.poly1d(z1)
fit2 = np.poly1d(z2)
fit3 = np.poly1d(z3)
fit4 = np.poly1d(z4)
fit5 = np.poly1d(z5)

y_new1 = fit1(x_slotframe)
y_new2 = fit2(x_slotframe)
y_new3 = fit3(x_slotframe)
y_new4 = fit4(x_slotframe)
y_new5 = fit5(x_slotframe)

plt.subplot(2, 1, 1)
#================ raw data ====================
plt.plot(x_slotframe[:300],y_numOfCell[:300],label='Schedule Cells')
plt.plot(x_slotframe[:300],y_packetInQueue[:300],label='Packets in queue')
plt.plot(x_slotframe[:300],y_sentPacket[:300],label='Sent packets')
# plt.plot(x_slotframe[:300],y_traffic[:300],label='traffic')
plt.plot(x_slotframe[:300],y_error[:300],label='Error')

#================  curve fitting ==============
# plt.plot(x_slotframe,y_new1,label='numOfCell')
# plt.plot(x_slotframe,y_new2,label='packetInQueue')
# plt.plot(x_slotframe,y_new3,label='sentPacket')
# plt.plot(x_slotframe,y_new4,label='traffic')
# plt.plot(x_slotframe,y_new5,label='error')

legend = plt.legend()

plt.xlim(slotframe[0], slotframe[300])
plt.xlabel('slotframe')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(x_slotframe[0:100],y_numOfCell[0:100],label='Schedule Cells')
plt.plot(x_slotframe[0:100],y_packetInQueue[0:100],label='Packets in queue')
plt.plot(x_slotframe[0:100],y_sentPacket[0:100],label='Sent packets')
# plt.plot(x_slotframe,y_traffic,label='traffic')
plt.plot(x_slotframe[0:100],y_error[0:100],label='Error')

legend = plt.legend()

plt.xlim(slotframe[0], slotframe[100])
plt.xlabel('slotframe')

plt.grid(True)

plt.show()
