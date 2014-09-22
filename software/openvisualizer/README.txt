.. Formatted as reStructuredText

OpenVisualizer is part of UC Berkeley's OpenWSN project. It provides 
monitoring, visualization, and debugging for an OpenWSN-based wireless sensor
network. See the project `home page`_ for more information.

Installation
------------
You may install OpenVisualizer with the standard pip command line, as shown
below. See the pip `installation instructions`_ if it is not installed 
already. You must be logged in with Windows administrator or Linux superuser
privileges to install to system-level directories.

::

    > pip install openVisualizer
    
Alternatively, you may download the OpenVisualizer archive, extract it, and
install with the standard Python setup.py command line, as shown below. This
command uses pip to retrieve other required Python libraries.

::

    > python setup.py install
    
Dependencies
------------
You also may need to separately install a driver for a USB-connected mote.
On Windows, a couple of other tools are required. See the OpenVisualizer 
`installation page`_ for a list.

Running, etc.
-------------
Once everything is installed, you may run the web interface, GUI, or command 
line utiltity as described on the OpenVisualizer home page. 

To uninstall a pip-based installation, use the command line::

    > pip uninstall openVisualizer

Please contact us via the `mailing list`_ or an `issue report`_ if you 
have any questions or suggestions.

| Thanks!
| The OpenWSN Team

.. _home page:
   https://openwsn.atlassian.net/wiki/display/OW/OpenVisualizer

.. _installation instructions:
   http://www.pip-installer.org/en/latest/installing.html

.. _installation page:
   https://openwsn.atlassian.net/wiki/display/OW/Installation+and+Dependencies

.. _mailing list: https://openwsn.atlassian.net/wiki/display/OW/Mailing+List

.. _issue report: https://openwsn.atlassian.net
