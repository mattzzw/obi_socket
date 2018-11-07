# obi_socket
Alternative firmware for the cheap OBI wifi socket based on an ESP8266

## Intro
There are several cheap wifi sockets around and most of them are already supported by excellent projects like [Tasmota](https://github.com/arendst/Sonoff-Tasmota) - including this socket.

However, the objective of this project is about creating a pyhon based software that provides a REST-like api to control the socket via http calls.

The hardware used is a 9€ power socket I bought from a hardware store ('OBI') in Germany. It seems to be a newer revision than the other OBI wifi sockets I found in the interwebs. But the basics are the same: LEDs, a button, a relay and an ESP8266.

More details about how to hack this socket can be found [in the wiki](https://github.com/mattzzw/obi_socket/wiki).

