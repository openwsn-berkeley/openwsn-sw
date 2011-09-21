#!/bin/bash

#set up opentunnel_4
modprobe ipv6
ip tunnel add opentunnel_4 mode sit remote 72.52.104.74 local `cat my_openipv4.txt` ttl 255
ip link set opentunnel_4 up
ip addr add 2001:470:1f04:fe3::2/64 dev opentunnel_4
ip route add ::/0 dev opentunnel_4
ip -f inet6 addr
