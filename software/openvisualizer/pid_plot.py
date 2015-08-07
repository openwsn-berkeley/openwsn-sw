#!/usr/bin/python

import string
import numpy as np
import matplotlib.pyplot as plt
import os

# ============== define ===================

# =============== structure ===============
slotframe = []
numOfCell = []
pidError  = []
        
# =============== prototype ===============

output = open('output.txt','r')
line = output.readline()
while line != '':
    if line[0]>='0' and line[0]<='9':
        data = line.split(',')
        slotframe.append(int(data[0]))
        numOfCell.append(int(data[1]))
        pidError.append(int(data[2]))
    line = output.readline()
output.close()
        
x_slotframe = np.int_(slotframe)
y_numOfCell = np.int_(numOfCell)
y_pidError  = np.int_(pidError) 

z1 = np.polyfit(x_slotframe,y_numOfCell,10)
z2 = np.polyfit(x_slotframe,y_pidError,10)

fit1 = np.poly1d(z1)
fit2 = np.poly1d(z2)

y_new1 = fit1(x_slotframe)
y_new2 = fit2(x_slotframe)

#================ raw data ====================
plt.plot(x_slotframe,y_numOfCell,label='numOfCell')
plt.plot(x_slotframe,y_pidError,label='pidError')

#================  curve fitting ==============
# plt.plot(x_slotframe,y_new1,label='numOfCell')
# plt.plot(x_slotframe,y_new2,label='pidError')

legend = plt.legend(shadow=True, fontsize='x-large')

plt.xlim(slotframe[0], slotframe[-1])
plt.xlabel('slotframe')
plt.title('pid test')

plt.show()
