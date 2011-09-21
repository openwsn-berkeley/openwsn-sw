from visual import *

file = open("channel_15.sensor","r")
imu_lines = file.readlines()
file.close

file = open("car.activity","r")
car_lines = file.readlines()
file.close

print str(len(imu_lines))+" imu lines"
print str(len(car_lines))+" car lines"

mag_vector = arrow(pos=(0,0,0), axis=(0,0,0), shaftwidth=0.5)
timestamp  = text()

sliding_window_size = 50

imu_line_number  = sliding_window_size+1
first_imu_time   = float(imu_lines[imu_line_number].split(' ')[0])
current_imu_time = float(imu_lines[imu_line_number].split(' ')[0])
#while (current_imu_time-first_imu_time<160):
#   imu_line_number  += 1
#   current_imu_time  = float(imu_lines[imu_line_number].split(' ')[0])

current_car_time        = 0
current_car_line_number = 0
current_car_present     = 0
while (imu_line_number<len(imu_lines)):
   rate(600)
   imu_line_number  += 1
   current_imu_time = float(imu_lines[imu_line_number].split(' ')[0])
   mag_x = 0
   mag_y = 0
   mag_z = 0
   for i in range(0,sliding_window_size):
      mag_x += float(imu_lines[imu_line_number-i].split(' ')[6])
      mag_y += float(imu_lines[imu_line_number-i].split(' ')[7])
      mag_z += float(imu_lines[imu_line_number-i].split(' ')[8])
   mag_x = mag_x/sliding_window_size
   mag_y = mag_y/sliding_window_size
   mag_z = mag_z/sliding_window_size
   while True:
      current_car_line_number += 1
      if (current_car_line_number<len(car_lines)):
         current_car_time         = float(car_lines[current_car_line_number].split(' ')[0])
         if (current_car_time>current_imu_time):
            current_car_line_number -= 1
            current_car_time         = float(car_lines[current_car_line_number].split(' ')[0])
            current_car_present      =   int(car_lines[current_car_line_number].split(' ')[1])
            break
      else:
         break
   if (current_car_present==1):
      mag_vector.color = color.red
   else:
      mag_vector.color = color.green
   print str(current_imu_time)+"\t"+str(current_imu_time-first_imu_time)
   mag_vector.axis = (mag_z, mag_x, mag_y)
