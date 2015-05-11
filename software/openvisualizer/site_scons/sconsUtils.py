from SCons.Script import *
import os
import platform

'''
Includes common SCons utilities, usable by SConstruct and any SConscript.
'''

def copySimfw(env, target):
    '''
    Copies the firmware Python extension module from where it was built in the
    openwsn-fw firmware repository, into the openVisualizerApp data/sim_files 
    directory tree. Stores architecture-specific module versions (amd64, x86)
    into an OS-specific subdirectory of sim_files. Also copies the file
    directly into the sim_files directory for local use if architecture and OS 
    match.
    
    Assumes the environment includes two entries:
    * 'FW_DIR'     entry with the path to the openwsn-fw repository
    * 'SIMHOSTOPT' architecture and OS of the extension module, like 'amd64-linux'
    
    :param target: Provides a unique pseudo-target for the Command to perform 
                   the copy.
    '''
    # in openwsn-fw, directory containing 'openwsnmodule_obj.h'
    incdir    = os.path.join(env['FW_DIR'],'bsp','boards','python')
    # in openwsn-fw, directory containing extension library
    libdir    = os.path.join(env['FW_DIR'],'build','python_gcc','projects','common')

    # Build source and destination pathnames.
    archAndOs = env['SIMHOSTOPT'].split('-')
    libext    = 'pyd' if archAndOs[1]=='windows' else 'so'
    srcname   = 'oos_openwsn.{0}'.format(libext)
    destname  = 'oos_openwsn-{0}.{1}'.format(archAndOs[0], libext)
    simdir    = os.path.join('bin', 'openVisualizerApp', 'sim_files')
    destdir   = os.path.join(simdir, archAndOs[1])
    
    cmdlist   = [
        Copy(simdir, os.path.join(incdir, 'openwsnmodule_obj.h')),
        Mkdir(os.path.join(destdir)),
        Copy(os.path.join(destdir, destname), os.path.join(libdir, srcname)),
    ]
                
    # Copy the module directly to sim_files directory if it matches this host.
    if archAndOs[0] == 'amd64':
        archMatch = platform.architecture()[0]=='64bit'
    else:
        archMatch = platform.architecture()[0]=='32bit'
    if archAndOs[1] == 'windows':
        osMatch = os.name=='nt'
    else:
        osMatch = os.name=='posix'

    if archMatch and osMatch:
        cmdlist.append( Copy(simdir, os.path.join(libdir, srcname)) )
    
    return env.Command(target, '', cmdlist)
        
