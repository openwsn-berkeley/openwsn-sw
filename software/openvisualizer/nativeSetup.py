from distutils.core import setup
import glob
from openvisualizer import ovVersion
from openvisualizer import appdirs

'''
This implementation of the traditional setup.py uses the application-level 
data_files parameter to store data files, rather than the package-level 
package_data parameter. We store these data files in operating system specific
, i.e. "native", locations with the help of the appdirs utility. For example,
shared data files on Linux are placed in "/usr/local/share/openvisualizer".

We use the site-level data and config directories because we expect the
superuser to run OpenVisualizer, so user-level directories like 
"/home/<user>/.config" are not available.

For native file storage to work, the installer *must not* modify the location 
of these files at install time.

Use of the legacy distutils package also accommodates existing Linux packaging 
tools.
'''

VERSION   = '.'.join([str(v) for v in ovVersion.VERSION])
datadir   = appdirs.site_data_dir('openvisualizer', 'OpenWSN')
confdir   = appdirs.site_config_dir('openvisualizer', 'OpenWSN')
webstatic = 'web_files/static'
webtmpl   = 'web_files/templates'
simdata   = 'sim_files'
with open('README.txt') as f:
    LONG_DESCRIPTION    = f.read()

def appdirGlob(globstr, subdir=''):
    appdir = 'bin/openVisualizerApp'
    if subdir == '':
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
    package_dir      = {'': '.', 'openvisualizer': 'openvisualizer'},
    scripts          = appdirGlob('openVisualizer*.py'),
    # Copy simdata files by extension so don't copy .gitignore in that directory.
    data_files       = [(confdir,                                  appdirGlob('*.conf')),
                        ('/'.join([datadir, webstatic, 'css']),                        appdirGlob('*', '/'.join([webstatic, 'css']))), 
                        ('/'.join([datadir, webstatic, 'font-awesome', 'css']),        appdirGlob('*', '/'.join([webstatic, 'font-awesome', 'css']))), 
                        ('/'.join([datadir, webstatic, 'font-awesome', 'fonts']),      appdirGlob('*', '/'.join([webstatic, 'font-awesome', 'fonts']))), 
                        ('/'.join([datadir, webstatic, 'images']),                     appdirGlob('*', '/'.join([webstatic, 'images']))), 
                        ('/'.join([datadir, webstatic, 'js']),                         appdirGlob('*.js', '/'.join([webstatic, 'js']))),
                        ('/'.join([datadir, webstatic, 'js', 'plugins', 'metisMenu']), appdirGlob('*', '/'.join([webstatic, 'js', 'plugins', 'metisMenu']))),
                        ('/'.join([datadir, webtmpl]),             appdirGlob('*', webtmpl)),
                        ('/'.join([datadir, simdata]),             appdirGlob('*.so', simdata)),
                        ('/'.join([datadir, simdata]),             appdirGlob('*.py', simdata)),
                        ('/'.join([datadir, simdata]),             appdirGlob('*.h', simdata))],
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