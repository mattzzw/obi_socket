#!/bin/sh

# Copies files in via webrepl_cli tool to esp8266

WEBREPL_CLI=../../esp8266/webrepl/webrepl_cli.py

PASSWD=Secret
OBI_SOCKET=192.168.1.122
#OBI_SOCKET=obi-socket1

# use 192.168.4.1 if available
ping -c 1 -W 10 192.168.4.1 &> /dev/null
if [ $? -eq 0 ]
then
   DEST_IP=192.168.4.1
else
   DEST_IP=$OBI_SOCKET
fi

for file in $@
do
    echo $file
    $WEBREPL_CLI -p $PASSWD $file $DEST_IP:/$file
done
