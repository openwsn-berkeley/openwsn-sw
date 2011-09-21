#!/bin/bash
cd /etc/network/if-up.d/openlbr/
rm -f openlbr.sh
wget http://openwsn.berkeley.edu/svn/software/openlbr/openlbr.sh
dos2unix openlbr.sh
chmod u+x openlbr.sh
screen -d -m /etc/network/if-up.d/openlbr/openlbr.sh
exit 0
