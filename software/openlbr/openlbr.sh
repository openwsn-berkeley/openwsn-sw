#!/bin/bash

#================================================ report address

#download
rm -f report_address.sh
wget http://openwsn.berkeley.edu/svn/software/openlbr/report_address.sh
dos2unix report_address.sh
chmod u+x report_address.sh

#run
./report_address.sh

#================================================ download files

cd /etc/network/if-up.d/openlbr/

rm -f *.pyc

#my_openipv4.txt (openlbr-specific)
rm -f ipv4_*
rm -f my_openipv4.txt
wget http://wsn.eecs.berkeley.edu/openserver/ipv4_`cat /etc/hostname`.txt
mv ipv4_`cat /etc/hostname`.txt my_openipv4.txt
dos2unix my_openipv4.txt

#my_opentunnel.sh (openlbr-specific)
rm -f opentunnel_*
rm -f my_opentunnel.sh
wget http://openwsn.berkeley.edu/svn/software/openlbr/opentunnel_`cat /etc/hostname`.sh
mv opentunnel_`cat /etc/hostname`.sh my_opentunnel.sh
dos2unix my_opentunnel.sh
chmod u+x my_opentunnel.sh

#my_openprefix.py (openlbr-specific)
rm -f openprefix_*
rm -f my_openprefix.py
wget http://openwsn.berkeley.edu/svn/software/openlbr/openprefix_`cat /etc/hostname`.py
mv openprefix_`cat /etc/hostname`.py my_openprefix.py
dos2unix my_openprefix.py
chmod u+x my_openprefix.py

#my_openradvd.conf (openlbr-specific)
rm -f openradvd_*
rm -f my_openradvd.conf
wget http://openwsn.berkeley.edu/svn/software/openlbr/openradvd_`cat /etc/hostname`.conf
mv openradvd_`cat /etc/hostname`.conf my_openradvd.conf
dos2unix my_openradvd.conf

#reload.sh
rm -f reload.sh
wget http://openwsn.berkeley.edu/svn/software/openlbr/reload.sh
dos2unix reload.sh
chmod u+x reload.sh

#openlbr.py
rm -f openlbr.py
wget http://openwsn.berkeley.edu/svn/software/openlbr/openlbr.py
dos2unix openlbr.py
chmod u+x openlbr.py

#================================================ setup

#tunnel
./my_opentunnel.sh

#tun kernel module
#echo tun >> /etc/modules
modprobe tun

#openlbr.py script
python openlbr.py 2>> error_log.txt
