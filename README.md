# obi_socket

Alternative firmware for the cheap OBI wifi socket based on an ESP8266.

- [Intro](#intro)
- [Hacking the Socket](#hacking-the-socket)
- [Web API](#web-api)
- [MQTT](#mqtt)

## Intro
There are several cheap wifi sockets around and most of them are already supported by excellent projects like [Tasmota](https://github.com/arendst/Sonoff-Tasmota) - including this socket.

However, the objective of this project is about creating a Python based software that provides a REST-like api to control the socket via http calls.

The software is based on [micropython](https://micropython.org/) and the [picoweb](https://github.com/pfalcon/picoweb) framework.

The hardware used is a 9€ power socket I bought from a hardware store ('OBI') in Germany. It seems to be a newer revision than the other OBI wifi sockets I found on the interwebs. The plastic case says something about EUROMATE GmbH.

But the basics are the same: LEDs, a button, a relay and an ESP8266. Yay.

![obi web socket](https://github.com/mattzzw/obi_socket/wiki/images/product.jpg)

## Hacking the Socket

More details about how to hack this socket can be found [in the wiki](https://github.com/mattzzw/obi_socket/wiki).

## Web API

### GET methods

| URI | Description |
|-----|-------------|
| `/switch?pwr=<on/off>` | switch power on/off |
| `/toggle?duration=<seconds>` | toggle power for x seconds, use `duration=0` to toggle only once |
| `/status` | returns port status as JSON |

### POST methods

| URI | Description |
|-----|-------------|
| `/restart` | restart socket |
| `/reset` | reset socket to default cfg |

## MQTT

On start-up the socket tries to connect to the mqtt server configured in `config.py`
and subscribes to the topic shown in the `/info` page.

```
mqtt_server = 'iot.eclipse.org'
```
Implemented actions are `on/off/toggle`.
