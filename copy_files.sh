#!/bin/sh

# Copies all python files in . via webrepl_cli tool

WEBREPL_CLI=../../esp8266/webrepl/webrepl_cli.py
PASSWD=Secret
IP=192.168.4.1

for file in *.py
do
    echo $file
    $WEBREPL_CLI -p $PASSWD $file $IP:/
done
