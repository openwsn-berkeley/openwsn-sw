#!/usr/bin/python

import os, time
import signal
import popen2
import filter
from scipy.signal import cheby2
from math import sqrt, atan2, sin, cos, tan
from Numeric import array
from quaternion import quatrotate, quatinv

xmax = 1024
ymax = 768

def flipy(y):
  return ymax-y-1

def dist(pt1, pt2):
  return sqrt(1.0*(pt1[0]-pt2[0])**2 + 1.0*(pt1[1]-pt2[1])**2)

def angle(pt0, pt1):
  return atan2(pt1[1]-pt0[1], pt1[0]-pt0[0])

class ir:
  p = None
  done = False

  x = [0,0,0,0]; 
  y = [0,0,0,0];
  r = [10,10,10,10];
  l = [0, 0, 0]

  origin = 0
  front = 1
  right = 2

  dx = 0
  dy = 0
  dz = 0
  psi = 0
  psifilter = filter.filter(cheby2(5,20,180.0/1000))

  xtarget = xmax/2
  ytarget = ymax/2
  ztarget = 200

  isvalid = 0

  header = "ir.xo " + \
           "ir.xf " + \
           "ir.xr " + \
           "ir.yo " + \
           "ir.yf " + \
           "ir.yr " + \
           "ir.dx " + \
           "ir.dy " + \
           "ir.dz " + \
           "ir.psi " + \
           "ir.isvalid"

  def __repr__(self):
    return repr(self.x[self.origin]) + " " + \
           repr(self.x[self.front]) + " " + \
           repr(self.x[self.right]) + " " + \
           repr(self.y[self.origin]) + " " + \
           repr(self.y[self.front]) + " " + \
           repr(self.y[self.right]) + " " + \
           repr(self.dx) + " " + \
           repr(self.dy) + " " + \
           repr(self.dz) + " " + \
           repr(self.psi) + " " + \
           repr(self.isvalid)

  def pt(self, index):
    return (self.x[index], self.y[index])

  def midpt(self, ind1, ind2):
    return ((self.x[ind1] + self.x[ind2])/2, (self.y[ind1] + self.y[ind2])/2)

  def go(self, data):
    self.x[0] = data[1]; self.y[0] = data[2]; s = data[3];
    self.x[0] += (s & 0x30) <<4; self.y[0] += (s & 0xC0) <<2;
    self.r[0] = s & 0x0f

    self.x[1] = data[4]; self.y[1] = data[5]; s = data[6];
    self.x[1] += (s & 0x30) <<4; self.y[1] += (s & 0xC0) <<2;
    self.r[1] = s & 0x0f

    self.x[2] = data[7]; self.y[2] = data[8]; s = data[9];
    self.x[2] += (s & 0x30) <<4; self.y[2] += (s & 0xC0) <<2;
    self.r[2] = s & 0x0f

    self.x[3] = data[10]; self.y[3] = data[11]; s = data[12];
    self.x[3] += (s & 0x30) <<4; self.y[3] += (s & 0xC0) <<2;
    self.r[3] = s & 0x0f

    self.y = map(flipy, self.y)

    if (self.x[3] == xmax-1 and self.y[3] == flipy(xmax-1) and \
        self.x[2] < xmax and self.y[2] >= 0):
      self.l[0] = dist(self.pt(2), self.pt(1))
      self.l[1] = dist(self.pt(2), self.pt(0))
      self.l[2] = dist(self.pt(1), self.pt(0))

      self.origin = self.l.index(max(self.l))
      self.right = self.l.index(min(self.l))
      self.front = 3 - self.origin - self.right

      self.dx = self.x[self.origin] - self.xtarget
      self.dy = self.y[self.origin] - self.ytarget
      self.dz = self.l[self.origin] - self.ztarget
      self.psi = self.psifilter.go(angle(self.pt(self.origin), self.pt(self.front)))
      self.isvalid = 1
      self.originvector()
    else:
      self.isvalid = 0
    '''
      self.dx = 0
      self.dy = 0
      self.dz = 0
      self.psi = 0
    '''

  def setx(self):
    self.xtarget = self.x[self.origin]

  def sety(self):
    self.ytarget = self.y[self.origin]

  def setz(self):
    self.ztarget = self.l[self.origin]

  rxb = 0
  ryb = 0
  rzb = 0

  def originvector(self): 
    lo = 0.087
    lr = 0.052
    lf = 0.070
    px2a = 7.431216648524430e-04

    do = dist(self.pt(self.origin), (0,0))
    theta = do * px2a
    r = lo / tan(self.l[self.origin] * px2a)
    self.rzb = -r * cos(theta)
    rp = r * sin(theta)
    self.rxb = rp * self.dx / do
    self.ryb = -rp * self.dy / do

  def location(self, q): 
    return -quatrotate(quatinv(q), array((self.rxb, self.ryb, self.rzb)))

