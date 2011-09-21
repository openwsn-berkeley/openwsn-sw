#!/usr/bin/python

class pid:
  kp = 0
  ki = 0
  kd = 0

  xd = 0
  xi = 0

  maxintegral = 100000

  def __init__(self,p,i,d):
    self.kp = p
    self.ki = i
    self.kd = d

  def reset(self):
    self.xi = 0
    self.xd = 0

  def go(self, x, dt):
    self.xi += x * dt;
    if (self.xi < -self.maxintegral):
      self.xi = -self.maxintegral
    if (self.xi > self.maxintegral):
      self.xi = self.maxintegral

    d = (x - self.xd) / dt
    self.xd = x

    return self.kp * x + self.ki * self.xi + self.kd * d
