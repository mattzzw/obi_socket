#!/bin/sh

# Copies files in via webrepl_cli tool to esp8266

WEBREPL_CLI=../../esp8266/webrepl/webrepl_cli.py
PASSWD=Secrect

#IP=192.168.4.1
IP=obi-socket1

for file in $@
do
    echo $file
    $WEBREPL_CLI -p $PASSWD $file $IP:/$file
done
