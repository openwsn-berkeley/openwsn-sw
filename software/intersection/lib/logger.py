#!/usr/bin/python

class logger:
  f = None
  fn = ""
  elems = []

  def __init__(self, fni):
    self.fn = fni

  def add(self, elem):
    self.elems.append(elem)

  def open(self):
    self.f = open(self.fn, "w")
    # self.f.write("ts, ")
    for elem in self.elems:
      self.f.write(" " + elem.header);
    self.f.write("\n")

  def go(self):
    # self.f.write(repr(ts) + ", ")
    for elem in self.elems:
      self.f.write(" " + repr(elem))
    self.f.write("\n")

  def close(self):
    self.f.close()
