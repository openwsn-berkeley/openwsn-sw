#!/usr/bin/python

from Numeric import array, dot, ones, zeros, concatenate, sum

lpf3a = [1,-4.8167274895740473,9.2833158430123568,-8.9486262034651780,4.3142478229542132,-.83220912344683795]
lpf3b = [1.3007957181818243e-02,-3.8857716848614235e-02,2.5850184407049528e-02,2.5850184407049396e-02,-3.8857716848614221e-02,1.3007957181818266e-02]
lpf3 = (lpf3b, lpf3a)

class filter:

  a = None
  b = None

  x = None
  y = None

  maxintegral = 100000

  def __init__(self, (bi, ai)):
    self.a = 1.0 * array(ai[1:]) / ai[0]
    self.b = 1.0 * array(bi) / ai[0]

  def reset(self):
    self.x = None
    self.y = None

  def go(self, xn):
    if (self.x == None):
      self.x = ones(len(self.b)) * xn * 1.0
      self.y = ones(len(self.a)) * xn * 1.0 * sum(self.b) / (1+sum(self.a))

    self.x = concatenate([[xn], self.x[:-1]])
    yn = dot(self.b, self.x) - dot(self.a, self.y)
    self.y = concatenate([[yn], self.y[:-1]])
    return yn
