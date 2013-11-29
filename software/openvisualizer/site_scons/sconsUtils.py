from SCons.Script import *
import os

'''
Includes common SCons utilities, usable by SConstruct and any SConscript.
'''

def copySimfw(env, target):
    '''
    Copies the firmware Python extension module from where it was built in the
    openwsn-fw firmware repository, into the openVisualizerApp data directory,
    which is software repository's home for data files.
    
    Assumes the environment includes an 'FW_DIR' entry with the path to the 
    openwsn-fw repository.
    
    :param target: Provides a unique pseudo-target for the Command to perform 
                   the copy.
    '''
    # in openwsn-fw, directory containing 'openwsnmodule_obj.h'
    incdir  = os.path.join(env['FW_DIR'], 'firmware','openos','bsp','boards','python')
    # in openwsn-fw, directory containing extension library
    libdir  = os.path.join(env['FW_DIR'], 'firmware','openos','projects','common')
    # extension of the library
    libext  = 'pyd' if sys.platform == 'win32' else 'so'
    # directory in openwsn-sw to copy the files into, relative to 
    # software/openvisualizer
    datadir = os.path.join('bin', 'openVisualizerApp', 'sim_files')
    
    return env.Command(
        target,
        '', 
        [
            Copy(datadir, os.path.join(incdir, 'openwsnmodule_obj.h')),
            Copy(datadir, os.path.join(libdir, 'oos_openwsn.{0}'.format(libext))),
        ]
    )

