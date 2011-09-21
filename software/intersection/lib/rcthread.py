#!/usr/bin/python

import pexpect
import time, signal
import threading
import copy
import filter

class rc (threading.Thread):
  filtb = [   0.138327096340138,  0.053305714450243,  0.175382929504086,  0.175382929504086,\
              0.053305714450243,  0.138327096340138]
  filta = [   1.000000000000000, -1.307757086627256,  1.377575940639513, -0.542414040121434,\
              0.206696290277178, -0.000069623579069]

  done = False
  rccur = [0, 0, 0, 0]
  rcdata = [0, 0, 0, 0]
  rcoffs = [76, 75, 0, 0]
  rcscal = [3, 3, 4, 5]
  rcbias = [43, 40, 0, 0]
  filts = [filter.filter((filtb, filta)), \
           filter.filter((filtb, filta)), \
           filter.filter((filtb, filta)), \
           filter.filter((filtb, filta))]

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
    threading.Thread.__init__(self)

  def run(self):
    alpha = 0.5 

    p = pexpect.spawn("exe/rcin", [], 1)
    first = True
    while (first and not self.done):
      try: self.rccur = map(int, p.readline().split())
      except (pexpect.TIMEOUT): pass
      else: self.rcoffs = copy.copy(self.rccur); first = False

    while (not self.done):
      try: self.rccur = map(int, p.readline().split())
      except (pexpect.TIMEOUT): pass
      else:
        for i in range(len(self.rccur)):
          self.rcdata[i] = int(self.filts[i].go(self.rccur[i] - self.rcoffs[i]))

    p.close()
    time.sleep(0.5)
    if p.isalive():
      time.sleep(0.5)
      p.kill(signal.SIGKILL)
    print "rcthread ended."

  def end(self):
    print "Ending rcthread..."
    self.done = True

  def val(self,i):
    v = self.rcdata[i]
    if v < 5 and v > -5:
      v = 0
    v = v * self.rcscal[i]
    v = v + self.rcbias[i]
    return v

  def rescale(self, i, d):
    self.rcscal[i] += d

  def recenter(self, i):
    self.rcoffs[i] = self.rccur[i]

  def recenterall(self):
    self.rcoffs = copy.copy(self.rccur)

if __name__ == '__main__':
  r = rc()
  r.start()
  while (not r.done):
    try:
      print repr(r)
    except (KeyboardInterrupt, SystemExit):
      r.end()
