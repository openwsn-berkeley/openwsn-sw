# -*- coding: utf-8 -*-
 
"""
Continuously read the serial port and process IO data received from a remote XBee.
"""

from xbee import XBee
import serial

ser = serial.Serial('/dev/ttyACM1', 115200)

xbee = XBee(ser)

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response
    except KeyboardInterrupt:
        break
        
ser.close()