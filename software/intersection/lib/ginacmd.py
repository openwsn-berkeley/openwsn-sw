#!/usr/bin/python

import sys, re, getopt, os

p_def = re.compile('^[\t ]*#([\t ]*)define[\t ]+CMD_([a-zA-Z0-9_]+)[\t ]+')

p_char = re.compile(r"'(\\.[^\\]*|[^\\])'")
p_hex = re.compile(r"0x([0-9a-fA-F]+)L?")

p_comment = re.compile(r'/\*([^*]+|\*+[^/])*(\*+/)?')
p_cpp_comment = re.compile('//.*')

ignores = [p_comment, p_cpp_comment]

def pytify(body):
  # replace ignored patterns by spaces
  for p in ignores:
    body = p.sub(' ', body)
  # replace char literals by ord(...)
  body = p_char.sub('ord(\\0)', body)
  # Compute negative hexadecimal constants
  start = 0
  UMAX = 2*(sys.maxint+1)
  while 1:
    m = p_hex.search(body, start)
    if not m: break
    s,e = m.span()
    val = long(body[slice(*m.span(1))], 16)
    if val > sys.maxint:
      val -= UMAX
      body = body[:s] + "(" + str(val) + ")" + body[e:]
    start = s + 1
  return body

class ginacmd:
  filename = ""
  listing = []

  def __init__(self,fn="lib/commands/commands.h"):
    self.filename = fn
    self.load()

  def list(self):
    for cmd in self.listing:
      print cmd[0], cmd[1]

  def load(self):

    fp = open(self.filename, 'r')

    curhead = ""
    curlist = []
    while 1:
      line = fp.readline()
      if not line: break
      match = p_def.match(line)
      if match:
        # gobble up continuation lines
        while line[-2:] == '\\\n':
          nextline = fp.readline()
          if not nextline: break
          line = line + nextline

        name = match.group(2).lower()
        body = pytify(line[match.end():]).strip()

        if match.group(1):
          setattr(self, name, eval(body))
          curlist.append(name)
        else:
          fnstr = "lambda y: [%s, y]" % body
          setattr(self, "cmd_" + name, eval(body))
          setattr(self, name, eval(fnstr))
          if curhead or curlist:
            self.listing.append([curhead, curlist])
          curhead = name
          curlist = []
    self.listing.append([curhead, curlist])
