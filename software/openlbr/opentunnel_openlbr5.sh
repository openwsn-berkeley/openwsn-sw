#!/bin/bash

#set up opentunnel_5
modprobe ipv6
ip tunnel add opentunnel_5 mode sit remote 72.52.104.74 local `cat my_openipv4.txt` ttl 255
ip link set opentunnel_5 up
ip addr add 2001:470:1f04:98e::2/64 dev opentunnel_5
ip route add ::/0 dev opentunnel_5
ip -f inet6 addr
