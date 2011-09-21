#!/usr/bin/python

import pygame
import sys
import time

class rc:
  rcval = [0, 0, 0, 0]
  rcdata = [0, 0, 0, 0]
  rcbias = [-45, -6, 0, 0]
  rcscal = [-3, 3, -10, 5]
  rcbuttons = []
  j = None

  header = "rc.ce " + \
           "rc.ca " + \
           "rc.cm " + \
           "rc.ct"

  def __repr__(self):
    return repr(self.val(0)) + " " + \
           repr(self.val(1)) + " " + \
           repr(self.val(2)) + " " + \
           repr(self.val(3))

  def __init__(self):
    pygame.init()
    pygame.joystick.init() # main joystick device system

    try:
      self.j = pygame.joystick.Joystick(0) # create a joystick instance
      self.j.init() # init instance
      # print 'Enabled joystick: ' + j.get_name()
    except pygame.error:
      sys.stderr.write('No joystick found.\n')

    for i in range(self.j.get_numbuttons()):
      self.rcbuttons.append(self.j.get_button(i))

  def val(self,ind):
    return int(self.rcval[ind])

  def go(self):
    if not self.j:
      return
    pygame.event.pump() 

    for i in range(len(self.rcdata)):
      self.rcdata[i] = 100 * self.j.get_axis(3-i)

    if self.j.get_button(7):
      self.rcbias[0] = 0
      self.rcbias[1] = 0

    if self.j.get_button(5):
      if not self.rcbuttons[5]:
        self.rcbias[0] = self.rcdata[0] + self.rcbias[0]
        self.rcbias[1] = self.rcdata[1] + self.rcbias[1]
        print repr(self.rcbias)
      self.rcdata[0] = 0
      self.rcdata[1] = 0

    if self.j.get_button(6):
      self.rcbias[2] = 0
      self.rcbias[3] = 0

    if self.j.get_button(4):
      if not self.rcbuttons[4]:
        self.rcbias[2] = self.rcdata[2] + self.rcbias[2]
        self.rcbias[3] = self.rcdata[3] + self.rcbias[3]
        print repr(self.rcbias)
      self.rcdata[2] = 0
      self.rcdata[3] = 0

    if self.j.get_button(0) and not self.rcbuttons[0]:
      self.rcbias[1] = self.rcbias[1] - 1
      print repr(self.rcbias)
    if self.j.get_button(1) and not self.rcbuttons[1]:
      self.rcbias[0] = self.rcbias[0] + 1
      print repr(self.rcbias)
    if self.j.get_button(2) and not self.rcbuttons[2]:
      self.rcbias[1] = self.rcbias[1] + 1
      print repr(self.rcbias)
    if self.j.get_button(3) and not self.rcbuttons[3]:
      self.rcbias[0] = self.rcbias[0] - 1
      print repr(self.rcbias)
        

    for i in range(len(self.rcbuttons)):
      self.rcbuttons[i] = self.j.get_button(i)

    for i in range(len(self.rcdata)):
      self.rcval[i] = self.rcscal[i] * (self.rcdata[i] + self.rcbias[i])

  def rescale(self, i, d):
    self.rcscal[i] += d

if __name__ == '__main__':
  r = rc()
  done = 0
  while (not done):
    try:
      r.go()
      print repr(r)
      time.sleep(.003)
    except (KeyboardInterrupt, SystemExit):
      done = 1
