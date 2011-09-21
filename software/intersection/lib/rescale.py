#!/usr/bin/python

import filter
from scipy.signal import cheby2

psc = 0.003308730168429; qsc = 0.003265541173168; rsc = 0.002927376610426; 

cax = 0.073575989318011; dax = -0.130935015466554
cay = 0.072470525838586; day = -0.167177628455709
caz = 0.071065088043540; daz = -0.064292674049229

# 2008 calibration
# mpc = 2339.525822367566; mpt = -0.549775222436125
# mqc = 2007.773520281689; mqt = -0.001829364560243
# mrc = 2061.504618230941; mrt = -0.017210583114712

# 2009 calibration
mpc = 2377.052017326490; mpt = -0.579350128759192
mqc = 1994.471223923883; mqt =  0.006303135211304
mrc = 2042.225534288070; mrt = -0.007693083497336

class rescale:
  p = 0; q = 0; r = 0;
  ax = 0; ay = 0; az = 0;

  ti = 0; ta = 0; rf = 0; rf1 = 0;

  tifilt = filter.filter(filter.lpf3)
  tafilt = filter.filter(filter.lpf3)
  rfilt = filter.filter(([0.25], [1.0, -0.75]))
  # rfilt = filter.filter(cheby2(5,20,180.0/1000))

  header = "rates.p " + \
           "rates.q " + \
           "rates.r " + \
           "rates.ax " + \
           "rates.ay " + \
           "rates.az " + \
           "rates.ti " + \
           "rates.ta " + \
           "rates.rf"

  def __repr__(self):
    return repr(self.p) + " " + \
           repr(self.q) + " " + \
           repr(self.r) + " " + \
           repr(self.ax) + " " + \
           repr(self.ay) + " " + \
           repr(self.az) + " " + \
           repr(self.ti) + " " + \
           repr(self.ta) + " " + \
           repr(self.rf)

  # def update(self, pin, qin, rin, ti, ta, axin, ayin, azin):
  def go(self, ginadata):
    pin = ginadata[1]
    qin = ginadata[2]
    rin = ginadata[3]
    self.ti = self.tifilt.go(ginadata[4])
    self.ta = self.tafilt.go(ginadata[5])
    axin = ginadata[7]
    ayin = -ginadata[6]
    azin = ginadata[8]

    mp = mpc + mpt * self.ti
    mq = mqc + mqt * self.ti
    mr = mrc + mrt * self.ta

    self.p = -(pin - mp) * psc
    self.q = -(qin - mq) * qsc
    self.r = -(rin - mr) * rsc
    self.rf = self.rfilt.go(self.r)
    # self.rf = self.rfilt.go(rin - mr)
    # self.rf1 = self.rfilt1.go(rin - mr)

    self.ax = cax * axin + dax
    self.ay = cay * ayin + day
    self.az = caz * azin + daz
