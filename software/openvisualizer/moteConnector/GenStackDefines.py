##
# Standalone script to generate the StackDefines.py file
# Double click to regenerate the file; assumes firmware/ lives next to software/
#
# \author Thomas Watteyne <watteyne@eecs.berkeley.edu>, August 2010
#

import os
import re
import time

OUTPUT_FILE         = 'StackDefines.py'
LOCATION_OPENWSN_H  = os.path.join('..','..','..','software','..','firmware','openos','openwsn')

def genComponentCodes():
    
    # find components code in openwsn.h
    codesFound = []
    for line in open(os.path.join(LOCATION_OPENWSN_H,'openwsn.h')):
        m = re.search('\s*COMPONENT_(\S*)\s*=\s*(\S*),\s*',line)
        if m:
            name = m.group(1)
            try:
                code = int(m.group(2),16)
            except ValueError:
                print "WARNING: {0} is not a hex number".format(m.group(2))
            else:
                codesFound.append((code,name))
    
    # turn into text
    output  = ["components = {"]
    output += ["{0:>4}: \"{1}\",".format(a,b) for (a,b) in codesFound]
    output += ["}"]
    output  = '\n'.join(output)
    
    return output

def genErrorDescriptions():
    
    # find components code in openwsn.h
    codesFound = []
    for line in open(os.path.join(LOCATION_OPENWSN_H,'openwsn.h')):
        m = re.search('\s*ERR_(\S*)\s*=\s*(\S*),\s*\/\/\s*([\S\s]*)',line)
        if m:
            name = m.group(1)
            desc = m.group(3).strip()
            try:
                code = int(m.group(2),16)
            except ValueError:
                print "WARNING: {0} is not a hex number".format(m.group(2))
            else:
                codesFound.append((code,desc))
    
    # turn into text
    output  = ["errorDescriptions = {"]
    output += ["{0:>4}: \"{1}\",".format(a,b) for (a,b) in codesFound]
    output += ["}"]
    output  = '\n'.join(output)
    
    return output

def main():

    # gather the information
    output  = []
    output += ["# DO NOT EDIT DIRECTLY!"]
    output += ["# This file was generated automatically by GenStackDefines.py"]
    output += ["# on {0}".format(time.strftime("%a, %d %b %Y %H:%M:%S"))]
    output += ["#"]
    output += [""]
    output += [genComponentCodes()]
    output += [""]
    output += [genErrorDescriptions()]
    output += [""]
    
    # write to file
    file = open(OUTPUT_FILE,'w')
    file.write('\n'.join(output))
    file.close
    
    raw_input('Script ended normally. Press enter to close.')

if __name__ == '__main__':
    main()