from setuptools     import setup
from setuptools.command.build_py import build_py as _build_py
import glob
import platform
import os
import shutil
from openvisualizer import ovVersion

'''
This implementation of the traditional setup.py uses the root package's 
package_data parameter to store data files, rather than the application-level 
data_files parameter. This arrangement organizes OpenVisualizer within a 
single tree of directories, and so is more portable.

In contrast to the native setup, the installer is free to relocate the tree
of directories with install options for setup.py.

This implementation is based on setuptools, and builds the list of module
dependencies by reading 'requirements.txt'.
'''

VERSION   = '.'.join([str(v) for v in ovVersion.VERSION])
webstatic = 'data/web_files/static'
webtmpl   = 'data/web_files/templates'
simdata   = 'data/sim_files'
with open('README.txt') as f:
    LONG_DESCRIPTION = f.read()
    
# Create list of required modules for 'install_requires' parameter. Cannot create
# this list with pip.req.parse_requirements() because it requires the pwd module,
# which is Unix only.
# Assumes requirements file contains only module lines and comments.
deplist = []
with open(os.path.join('openvisualizer', 'data', 'requirements.txt')) as f:
    for line in f:
        if not line.startswith('#'):
            deplist.append(line)

def appdirGlob(globstr, subdir=''):
    appdir = 'bin/openVisualizerApp'
    if subdir == '':
        return glob.glob('/'.join([appdir, globstr]))
    else:
        return glob.glob('/'.join([appdir, subdir, globstr]))
        
class build_py(_build_py):
    '''
    Extends setuptools build of openvisualizer package data at installation time.
    Selects and copies the architecture-specific simulation module from an OS-based 
    subdirectory up to the parent 'sim_files' directory. Excludes the OS subdirectories
    from installation.
    '''
    def build_package_data(self):
        _build_py.build_package_data(self)

        osname  = 'windows' if os.name=='nt' else 'linux'
        suffix  = 'amd64' if platform.architecture()[0]=='64bit' else 'x86'
        fileExt = 'pyd' if os.name=='nt' else 'so'

        simPath = None
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                moduleName = 'oos_openwsn-{0}.{1}'.format(suffix, fileExt)
                modulePath = os.path.join(osname, moduleName)
                if package == 'openvisualizer' and filename.endswith(modulePath):
                    srcfile  = os.path.join(src_dir, filename)
                    simPath  = os.path.join(build_dir, 'data', 'sim_files')
                    target   = os.path.join(simPath, 'oos_openwsn.{0}'.format(fileExt))
                    self.copy_file(srcfile, target)
        
        if simPath:
            shutil.rmtree(os.path.join(simPath, 'linux'))
            shutil.rmtree(os.path.join(simPath, 'windows'))

setup(
    name             = 'openVisualizer',
    packages         = ['openvisualizer', 
                        'openvisualizer.BspEmulator', 'openvisualizer.eventBus', 
                        'openvisualizer.lbrClient', 'openvisualizer.moteConnector', 
                        'openvisualizer.moteProbe', 'openvisualizer.moteState', 
                        'openvisualizer.openLbr', 'openvisualizer.openTun', 
                        'openvisualizer.openType', 'openvisualizer.openUI',
                        'openvisualizer.RPL', 'openvisualizer.SimEngine', 'openvisualizer.remoteConnectorServer'],
    scripts          = appdirGlob('openVisualizer*.py'),
    package_dir      = {'': '.', 'openvisualizer': 'openvisualizer'},
    # Copy simdata files by extension so don't copy .gitignore in that directory.
    package_data     = {'openvisualizer': [
                        'data/*.conf',
                        'data/requirements.txt',
                        '/'.join([webstatic, 'css', '*']), 
                        '/'.join([webstatic, 'font-awesome', 'css', '*']), 
                        '/'.join([webstatic, 'font-awesome', 'fonts', '*']), 
                        '/'.join([webstatic, 'images', '*']), 
                        '/'.join([webstatic, 'js', '*.js']), 
                        '/'.join([webstatic, 'js', 'plugins', 'metisMenu', '*']), 
                        '/'.join([webtmpl, '*']), 
                        '/'.join([simdata, 'windows', '*.pyd']), 
                        '/'.join([simdata, 'linux',   '*.so']), 
                        '/'.join([simdata, '*.h']) 
                        ]},
    install_requires = deplist,
    # Must extract zip to edit conf files.
    zip_safe         = False,
    version          = VERSION,
    author           = 'Thomas Watteyne',
    author_email     = 'watteyne@eecs.berkeley.edu',
    description      = 'Wireless sensor network monitoring, visualization, and debugging tool',
    long_description = LONG_DESCRIPTION,
    url              = 'https://openwsn.atlassian.net/wiki/display/OW/OpenVisualizer',
    keywords         = ['6TiSCH','Internet of Things','6LoWPAN','802.15.4e','sensor','mote'],
    platforms        = ['platform-independent'],
    license          = 'BSD 3-Clause',
    classifiers      = [
                       'Development Status :: 3 - Alpha',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 2.7',
                       'Topic :: Communications',
                       'Topic :: Home Automation',
                       'Topic :: Internet',
                       'Topic :: Software Development',
                       ],
    cmdclass           = {'build_py' : build_py},
)
