import machine
import ubinascii

# Ports
outputs           = {   1: { 'pin':  4, 'active': 'high', 'obj' : ''},  # relay port 1
                        2: { 'pin': 12, 'active': 'high', 'obj' : ''},  # LED green
                        3: { 'pin': 13, 'active': 'high', 'obj' : ''}   # LED red
                        }
inputs            = {   1: { 'pin':  5}}  # on/off switch


# Consts
RELAY = 1
LED_G = 2
LED_R = 3
ON_OFF = 1


# FIXME - move the following cfg to obi_socket.cfg in json format

# Password to access esp's access point for setup
ap_password = "myobiPassword"

# time zone offset (UTC+x) in seconds
tz_offset = 3600

# MQTT config
mqtt_client_id = ubinascii.hexlify(machine.unique_id()).decode()
mqtt_server = 'iot.eclipse.org'
mqtt_sub_topic = mqtt_client_id + '/' + 'switch/action'
mqtt_pub_topic = mqtt_client_id + '/' + 'switch/status'
