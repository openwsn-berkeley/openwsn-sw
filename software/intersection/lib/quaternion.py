#!/usr/bin/python

from math import sin, cos, tan, pi
from Numeric import array, dot

def quat2dcm(q):
  dcm = array(((0,0,0),(0,0,0),(0,0,0))) * 1.0

  dcm[0,0] = q[0]**2 + q[1]**2 - q[2]**2 - q[3]**2;
  dcm[0,1] = 2.*(q[1]*q[2] + q[0]*q[3]);
  dcm[0,2] = 2.*(q[1]*q[3] - q[0]*q[2]);
  dcm[1,0] = 2.*(q[1]*q[2] - q[0]*q[3]);
  dcm[1,1] = q[0]**2 - q[1]**2 + q[2]**2 - q[3]**2;
  dcm[1,2] = 2.*(q[2]*q[3] + q[0]*q[1]);
  dcm[2,0] = 2.*(q[1]*q[3] + q[0]*q[2]);
  dcm[2,1] = 2.*(q[2]*q[3] - q[0]*q[1]);
  dcm[2,2] = q[0]**2 - q[1]**2 - q[2]**2 + q[3]**2;

  return dcm

def quatinv(q):
  q = -q
  q[0] = -q[0]
  return q

def eul2quat(ph, th, psi):
  cp = cos(ph/2.0); ct = cos(th/2.0); cs = cos(psi/2.0)
  sp = sin(ph/2.0); st = sin(th/2.0); ss = sin(psi/2.0)

  return array((
    cp * ct * cs + sp * st * ss,
    sp * ct * cs - cp * st * ss,
    cp * st * cs + sp * ct * ss,
    cp * ct * ss - sp * st * cs
  ))

def quatrotate(q, v):
  return(dot(quat2dcm(q), v))
