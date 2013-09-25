# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below, 
# where both the copyright owner and organization are the Regents of the  
# University of California. 
# https://openwsn.atlassian.net/wiki/display/OW/License

'''
Helper module to fix the Python path.

There are different ways to run the OpenVisualizer:
- from SCons (e.g. "scons rungui"), in which case the project is run from the
   openvisualizer/ root directory
- by double-clicking on the OpenVisualizerGui.py or OpenVisualizerCli.py files,
   in which case, the program is run from the
   openvisualizer\bin\openVisualizerApp directory.

The function below ensure that, if the program is run by double-clicking, the
Python PATH is set up correctly.
'''

import sys
import os

def updatePath():
    '''
    This function determines whether the program is run from SCons or from the
    source file. In the former case, the path is already set up correctly. In
    the latter case, this function adjusts the path.
    '''
    
    # I'm assuming I'll have to update the path
    updatePath = True
    
    # do NOT update if running from SCons
    # TODO: this methid is relatively fragile
    uiFile = sys.argv[0]
    if uiFile.startswith('bin'):
        updatePath = False
    
    # update the path, if needed
    if updatePath:
        here = sys.path[0]
        sys.path.insert(0,os.path.join('..','..','..','openwsn-fw','firmware','openos','projects','common')) # emulated mote
        sys.path.insert(0,os.path.join('..','..','..'))                            # openvisualizer/software/
        sys.path.insert(0,os.path.join('..','..','..', 'openUI')),                 # openvisualizer/software/openUI
        sys.path.insert(0,os.path.join('..','..')),                                # openvisualizer/
        sys.path.insert(0,os.path.join('..','..','eventBus','PyDispatcher-2.0.3')),# openvisualizer/eventBus/PyDispatcher-2.0.3
