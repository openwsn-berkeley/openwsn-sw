OpenVisualizer is part of UC Berkeley's OpenWSN project. It provides 
monitoring, visualization, and debugging for an OpenWSN-based wireless sensor
network. See the project home page for more information [1].

You may install OpenVisualizer with the standard pip command line, as shown
below. See the pip installation instructions if it is not installed already 
[2]. You must be logged in with administrator/superuser privileges to install
to system-level directories.

    > pip install openVisualizer
    
Alternatively, you may download the OpenVisualizer archive, extract it, and
install with the standard Python setup.py command line, as shown below. This
command uses pip to retrieve other required Python libraries.

    > python setup.py install

You also may need to separately install a driver for a USB-connected mote.
On Windows, a couple of other tools are required. See the OpenVisualizer 
installation page [3]. Once everything is installed, you may run the web 
interface, GUI, or command line utiltity as described on the OpenVisualizer 
home page. 

To uninstall a pip-based installation, use the command line:

    > pip uninstall openVisualizer

Please contact us via the mailing list [4] or an issue report [5] if you have
any questions or suggestions.

Thanks!
The OpenWSN Team

[1] https://openwsn.atlassian.net/wiki/display/OW/OpenVisualizer
[2] http://www.pip-installer.org/en/latest/installing.html
[3] https://openwsn.atlassian.net/wiki/display/OW/Installation+and+Dependencies
[4] https://openwsn.atlassian.net/wiki/display/OW/Mailing+List
[5] https://openwsn.atlassian.net
