from distutils.core import setup
import glob
from openvisualizer import ovVersion

'''
This implementation of the traditional setup.py uses the root package's 
package_data parameter to store data files, rather than the application-level 
data_files parameter. This arrangement organizes OpenVisualizer within a 
single tree of directories, and so is more portable.

In contrast to the native setup, the installer is free to relocate the tree
of directories with install options for setup.py.
'''

VERSION   = '.'.join([str(v) for v in ovVersion.VERSION])
webstatic = 'data/web_files/static'
webtmpl   = 'data/web_files/templates'
simdata   = 'data/sim_files'
with open('README.txt') as f:
    LONG_DESCRIPTION = f.read()

def appdirGlob(globstr, subdir=''):
    appdir = 'bin/openVisualizerApp'
    if (subdir == ''):
        return glob.glob('/'.join([appdir, globstr]))
    else:
        return glob.glob('/'.join([appdir, subdir, globstr]))

setup(
    name             = 'openVisualizer',
    packages         = ['openvisualizer', 
                        'openvisualizer.BspEmulator', 'openvisualizer.eventBus', 
                        'openvisualizer.lbrClient', 'openvisualizer.moteConnector', 
                        'openvisualizer.moteProbe', 'openvisualizer.moteState', 
                        'openvisualizer.openLbr', 'openvisualizer.openTun', 
                        'openvisualizer.openType', 'openvisualizer.openUI', 
                        'openvisualizer.RPL', 'openvisualizer.SimEngine'],
    scripts          = appdirGlob('openVisualizer*.py'),
    package_dir      = {'': '.', 'openvisualizer': 'openvisualizer'},
    # Copy simdata files by extension so don't copy .gitignore in that directory.
    package_data     = {'openvisualizer': [
                        'data/*.conf',
                        '/'.join([webstatic, '*.css']), 
                        '/'.join([webstatic, '*.js']), 
                        '/'.join([webstatic, '*.png']),
                        '/'.join([webstatic, 'images', '*']), 
                        '/'.join([webtmpl, '*']), 
                        '/'.join([simdata, '*.pyd']), 
                        '/'.join([simdata, '*.so']), 
                        '/'.join([simdata, '*.h']), 
                        ]},
    version          = VERSION,
    author           = 'Thomas Watteyne',
    author_email     = 'watteyne@eecs.berkeley.edu',
    description      = 'OpenWSN wireless sensor network monitoring, visualization, and debugging tool',
    long_description = LONG_DESCRIPTION,
    url              = 'http://www.openwsn.org/',
    keywords         = ['6TiSCH','Internet of Things','6LoWPAN','sensor','mote'],
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
)