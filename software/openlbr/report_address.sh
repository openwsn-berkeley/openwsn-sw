#!/bin/bash

#================================================ report address

wget -O - http://wsn.eecs.berkeley.edu/openserver/record_openlbr_ipv4.php?hostname=`cat /etc/hostname`

