#!/usr/bin/python

import rescale
from quaternion import eul2quat, quatinv, quatrotate
from math import sin, cos, tan, pi
from Numeric import array, dot, transpose, identity, reshape
from LinearAlgebra import inverse


class kfstate:
  phi = 0.0; theta = 0.0; psi = 0.0
  vx = 0.0; vy = 0.0; vz = 0.0

  ab = [0, 0, -1]
  ae = [0, 0, 0]
  ve = [0, 0, 0]
  quat = array((1, 0, 0, 0))
  # dcmb2e = None

  pmat = identity(2)/100.0
  Q = array(((4.9e-5, 0), (0, 2.1e-5)))
  R = array(((8.1e-4, 0, 0), (0, 7.9e-4, 0), (0, 0, 1.6e-3)))

  # thetafilter = filter.filter(filter.lpf3b, filter.lpf3a)

  header = "states.phi " + \
           "states.theta " + \
           "states.psi " + \
           "states.vex " + \
           "states.vey " + \
           "states.vez" 

  def __repr__(self):
    return repr(self.phi) + " " + \
           repr(self.theta) + " " + \
           repr(self.psi) + " " + \
           repr(self.ve[0]) + " " + \
           repr(self.ve[1]) + " " + \
           repr(self.ve[2])

  def reset(self):
    self.phi = 0.0
    self.theta = 0.0
    self.psi = 0.0
    self.ve = [0, 0, 0]

  def kfupdate(self, dt, rs):
    self.ab  = array((rs.ax, -rs.ay, -rs.az))

    ph = self.phi
    th = self.theta
    P  = self.pmat

    A  = array(((-rs.q*cos(ph)*tan(th)+rs.r*sin(ph)*tan(th), (-rs.q*sin(ph)+rs.r*cos(ph))/(cos(th)*cos(th))),
                (rs.q*sin(ph)-rs.r*cos(ph)                 , 0)))

    dph = rs.p - rs.q*sin(ph)*tan(th) - rs.r*cos(ph)*tan(th)
    dth =      - rs.q*cos(ph)         - rs.r*sin(ph)
    dP  = dot(A, P) + dot(P, transpose(A)) + self.Q

    ph = ph + dph * dt
    th = th + dth * dt
    P  = P  + dP  * dt

    Cx = array((0               , cos(th)))
    Cy = array((-cos(th)*cos(ph), sin(th)*sin(ph)))
    Cz = array((cos(th)*sin(ph) , sin(th)*cos(ph)))
    C  = array((Cx, Cy, Cz))

    L = dot(dot(P, transpose(C)), inverse(self.R + dot(dot(C, P), transpose(C))))
    h = array((sin(th), -cos(th)*sin(ph), -cos(th)*cos(ph)))

    P  = dot(identity(2) - dot(L, C), P)
    ph = ph + dot(L[0], self.ab - h)
    th = th + dot(L[1], self.ab - h) 

    ph = ((ph+pi) % (2*pi)) - pi;
    th = ((th+pi) % (2*pi)) - pi;

    self.pmat  = P
    self.phi   = ph 
    self.theta = th

    psidot = rs.q * sin(ph) / cos(th) + rs.r * cos(ph) / cos(th);
    self.psi += psidot * dt;

    self.quat = eul2quat(ph,th,self.psi)
    # self.dcmb2e = quat2dcm(quatinv(self.quat))

    # self.ae = dot(self.dcmb2e, self.ab)
    self.ae = quatrotate(quatinv(self.quat), self.ab)
    self.ae[2] = -self.ae[2]-1
    self.ae[1] = -self.ae[1]

    self.ve += self.ae * dt * 9.81
