#!/bin/bash

#kill possible previously running screen sessions
kill -9 `ps -aef | grep 'SCREEN' | grep -v grep | awk '{print $2}'`
#kill possible previously running python script
kill -9 `ps -aef | grep 'python' | grep -v grep | awk '{print $2}'`

python openlbr.py 2>> error_log.txt
