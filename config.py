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

unique_machine_id = ubinascii.hexlify(machine.unique_id()).decode()
initial_hostname = "obi-socket-{}".format(unique_machine_id)

initial_cfg = {
                'hostname':         initial_hostname,
                'wifi_ssid':        '',
                'wifi_pw':          '',
                'ap_pw':            'myobiPassword',
                'tz_offset':        3600,
                'mqtt_enable':      True,
                'mqtt_cid':          unique_machine_id,
                'mqtt_server':      'iot.eclipse.org',
                'mqtt_user':        '',
                'mqtt_pw':          '',
                'mqtt_subt':        unique_machine_id + '/' + 'switch/action',
                'mqtt_pubt':        unique_machine_id + '/' + 'switch/status'
}

# ----------------------------------------------------------------------------
