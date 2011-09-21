import os, sys
import glob

graph_height = 2.5

#list all the channels
channels = glob.glob('*.sensor')
for i in range(0,len(channels)):
   channels[i] = channels[i].rstrip('.sensor')

#list all the activities
activities = glob.glob('*.activity')
for i in range(0,len(activities)):
   activities[i] = activities[i].rstrip('.activity')

for channel in channels:
   # get name of the sensors from header line
   f = open(channel+".sensor", 'r')
   sensor_names = f.readline().split(' ')
   f.close()
   # get min_*, max_* for all sensors
   min_values = []
   max_values = []
   for sensor_name in sensor_names:
      min_values.append('')
      max_values.append('')
   f = open(channel+".sensor", 'r')
   lines = f.readlines()
   lines = lines[1:] #skip the header line
   for line in lines:
      for (key,sensor_name) in enumerate(sensor_names):
         try:
            sensor_value = float((line.split(' '))[key])
         except:
            print sys.exc_info()
            print "problem reading "+sensor_name
            pass
         else:
            if (sensor_value<min_values[key] or min_values[key]==''):
               min_values[key] = sensor_value
            if (sensor_value>max_values[key] or max_values[key]==''):
               max_values[key] = sensor_value
   f.close()
   print '======================================================'
   print 'channel='+str(channel)
   print 'min_values='+str(min_values)
   print 'max_values='+str(max_values)
   print '======================================================'
   # create *.plot
   gnuplot_commands  = "set style line 1 lt 1 lc rgb \"red\"  lw 1\n"
   gnuplot_commands += "set style line 2 lt 1 lc rgb \"blue\" lw 3\n"
   gnuplot_commands += "set term postscript eps enhanced color\n"
   gnuplot_commands += "set output \""+channel+".eps\"\n"
   gnuplot_commands += "set multiplot\n"
   gnuplot_commands += "\n"
   gnuplot_commands += "set rmargin 0\n"
   gnuplot_commands += "set lmargin 0\n"
   gnuplot_commands += "set tmargin 0\n"
   gnuplot_commands += "set bmargin 0\n"
   gnuplot_commands += "\n"
   gnuplot_commands += "set xrange [0:"+str(float(max_values[0])-float(min_values[0]))+"]\n"
   x_axis_drawn = 0
   for (key,activity) in enumerate(activities):
      gnuplot_commands += "\n"
      gnuplot_commands += "set yrange [-0.05:1.05]\n"
      gnuplot_commands += "set format y \"\"\n"
      if (x_axis_drawn==0):
         gnuplot_commands += "set format x \"%.2f\"\n"
         x_axis_drawn = 1
      else:
         gnuplot_commands += "set format x \"\"\n"
      gnuplot_commands += "set size   0.92,"+str(0.8       *graph_height/(float(len(sensor_names)+len(activities))-1.0))+"\n"
      gnuplot_commands += "set origin 0.07,"+str(float(key)*graph_height/(float(len(sensor_names)+len(activities))-1.0))+"\n"
      gnuplot_commands += "plot \""+activity+".activity\" u ($1-"+str(min_values[0])+"):2 w lines ls 2 title \""+activity+"\"\n"
   for (key,sensor_name) in enumerate(sensor_names):
      if (sensor_name!='timestamp'):
         gnuplot_commands += "\n"
         gnuplot_commands += "set yrange ["+str(min_values[key])+":"+str(max_values[key])+"]\n"
         gnuplot_commands += "set format y \"%.2f\"\n"
         if (x_axis_drawn==0):
            gnuplot_commands += "set format x \"%.2f\"\n"
            x_axis_drawn = 1
         else:
            gnuplot_commands += "set format x \"\"\n"
         gnuplot_commands += "set size   0.92,"+str(0.8       *graph_height/(float(len(sensor_names)+len(activities))-1.0))+"\n"
         gnuplot_commands += "set origin 0.07,"+str(float(key+len(activities)-1)*graph_height/(float(len(sensor_names)+len(activities))-1.0))+"\n"
         gnuplot_commands += "plot \""+channel+".sensor\" u ($1-"+str(min_values[0])+"):"+str(key+1)+" w lines ls 1 title \'"+sensor_name+"\'\n"
   f = open(channel+".plot", 'w')
   f.write(gnuplot_commands)
   f.close()
   #plot
   if (os.name=='nt'):
      os.system("C:\gnuplot\\bin\pgnuplot "+channel+".plot")
   elif (os.name=='posix'):
      os.system("gnuplot "+channel+".plot")
