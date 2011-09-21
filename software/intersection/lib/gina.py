#!/usr/bin/python

import os, time, sys
import signal
import popen2
import threading
import pid
import rescale
import kfstate
import logger
import ircam
import motetalk
import rcthread
from scipy.signal import cheby2

def threshold(val, minv, maxv):
  if val < minv: val = minv
  if val > maxv: val = maxv
  return val

def splitbytes(val):
  val_dh = (val >> 8) & 0xff
  val_dl = val & 0xff
  return (val_dh, val_dl)

def setpwm(LEDg, LEDo, mot1, mot0, srv1, srv2, srv3): # generates serial output string
  # check imputs and correct input if necassary
  if LEDg <= 0: LEDg = 0
  else: LEDg = 1

  if LEDo <= 0: LEDo = 0
  else: LEDo = 1

  mot0 = threshold(mot0, 0, 800)
  mot1 = threshold(mot1, 0, 800)
  srv1 = threshold(srv1, -1000, 1000)
  srv2 = threshold(srv2, -1000, 1000)
  srv3 = threshold(srv3, -1000, 1000)

  # calculate bytes
  (mot0_dh, mot0_dl) = splitbytes(mot0)
  (mot1_dh, mot1_dl) = splitbytes(mot1)

  (srv1_dh, srv1_dl) = splitbytes(srv1)
  (srv2_dh, srv2_dl) = splitbytes(srv2)
  srv3 = (srv3<<4)+((1-LEDg)<<1)+(1-LEDo)
  (srv3_dh, srv3_dl) = splitbytes(srv3)
  return [mot1_dl, mot1_dh, mot0_dl, mot0_dh, srv1_dl, srv1_dh, srv2_dl, srv2_dh, srv3_dl, srv3_dh]

def restring(data):
  # heli
  m = data.pop(6)
  t = data.pop(7)
  t += (data.pop(8) << 8)
  data.append(m)
  data.append(t)

  return data

class gina (threading.Thread):
  done = False

  rc = None
  mote = None
  rates = rescale.rescale()
  states = kfstate.kfstate()
  ir = ircam.ir()

  ca = 0; ce = 0; cm = 0; ct = 0;
  pl = 0;
  oled = 1; gled = 0;

  lastt = 0; lastn = 0
  line = ""

  log = logger.logger("data/" + time.strftime("%Y%m%d-%H%M%S"))

  header = "pid.yg pid.pg pid.rg pid.mg"

  moteheader = "n p q r ti ta cm x ct1 y ct2 z ir0 ir1 ir2 ir3 ir4 ir5 ir6 ir7 ir8 ir9 ira irb irc ca ce"
  motefmt = 'x H H H H H  H  H  b B   b B   b B   B   B   B   B   B   B   B   B   B   B   B   B   H  H'

  def __repr__(self):
    return repr(self.yg) + " " + \
           repr(self.pg) + " " + \
           repr(self.rg) + " " + \
           repr(self.mg)

  def run(self):
    self.rc = rcthread.rc()
    self.mote = motetalk.motetalk(motefmt, moteheader)
    self.rc.start()

    self.log.add(self)
    self.log.add(self.rc)
    self.log.add(self.mote)
    self.log.add(self.rates)
    self.log.add(self.states)
    self.log.add(self.ir)
    self.log.open()

    mote.newline()

    while (not self.done):
      (data, ts) = mote.nextline()
      if (data):
        arr = restring(data)

        dt = data[0] - self.lastn
        if dt > 0 and dt < 11:
          dt = dt * .003
        else:
          dt = ts - self.lastt
        self.lastt = ts
        self.lastn = data[0]

        ginadata = data[0:9]
        irdata = data[9:]

        self.ir.go(irdata)
        self.rates.go(ginadata)

        self.states.kfupdate(dt, self.rates)
        self.setout(dt)

        self.log.go();

        if self.pl < 0:
          self.pl += 4
      else: self.gled = 0

    self.rc.end()
    self.mote.end()

    self.log.close()
    sys.stderr.write("gina ended.\n")

  # kpcyclic = 2.0
  # main = pid.pid(2, 0.0, 0.0)
  # pitch = pid.pid(kpcyclic, 0.0, 0.0)
  # roll = pid.pid(kpcyclic, 0.0, 0.0)
  yaw = pid.pid(0, 1.0, 0.0)
  psid = 0
  yaw2 = pid.pid(15., 40., 0.0)

  mg = 0
  yg = 0
  pg = 0
  rg = 0

  def setout(self, dt):
    e = self.rc.val(0)
    a = self.rc.val(1)
    m = self.rc.val(2)
    t = self.rc.val(3)

    self.yg = int(self.yaw2.go(self.rates.rf - t/300, dt))
    # self.yg += int(self.yaw.go(-self.ir.psi, dt))
    self.psid = self.yaw.go(-t/50, dt)
    '''
    self.yg = 10 * self.rates.rf + \
              50 * self.ir.isvalid * self.ir.psi + \
              50 * (self.states.psi - self.psid)
    '''

    self.mg = m
    # self.mg += 2 * self.ir.isvalid * self.ir.dz

    self.pg = -200 * self.states.theta
    if (abs(self.states.theta) < 0.1):
      self.pg += 2 * self.ir.isvalid * self.ir.dx

    self.rg = 200 * (self.states.phi-.1)
    if (abs(self.states.phi) < 0.1):
      self.rg += 2 * self.ir.isvalid * self.ir.dy

    '''
    e = e + self.pg
    a = a + self.rg
    '''

    if m == 0:
      self.yaw2.reset()
      # self.yaw.reset()
      # self.pitch.reset()
      # self.roll.reset()
      t = 0

    else: 
      # m is bottom, t is top
      m = self.mg - self.yg/2
      t = self.mg + self.yg

      # m = self.cm - self.ct
      # t = self.cm + self.ct
      # e = int(self.pitch.go(self.thetaf + (self.ce / self.kpcyclic), dt))
      # a = int(self.roll.go(self.phif + (self.ca / self.kpcyclic), dt))

    self.mote.send([7, setpwm(self.oled, self.gled, m, t, e, a, self.pl)])

  def drop(self):
    self.pl = -1000

  def end(self):
    sys.stderr.write("Ending gina...\n")
    self.done = True

  def reset(self):
    self.states.reset()
    # self.yaw.reset()
    # self.pitch.reset()
    # self.roll.reset()

if __name__ == '__main__':
  g = gina()
  g.start()
  while (not g.done):
    try:
      sys.stdout.write(".")
    except (KeyboardInterrupt, SystemExit):
      g.end()
