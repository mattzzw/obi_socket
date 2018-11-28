import machine
import ubinascii

# Ports
outputs           = {   1: { 'pin': 15, 'active': 'high', 'obj' : ''},  # relay port 1
                        2: { 'pin': 2, 'active': 'low', 'obj' : ''},  # LED green
                        3: { 'pin': 0, 'active': 'low', 'obj' : ''}   # LED red
                        }
inputs            = {   1: { 'pin':  13}}  # on/off switch


# Consts
RELAY = 1
LED_G = 2
LED_R = 3
ON_OFF = 1

unique_machine_id = ubinascii.hexlify(machine.unique_id()).decode()
initial_hostname = "obi-socket-{}".format(unique_machine_id[:6])

initial_cfg = {
                'hostname':         initial_hostname,
                'wifi_ssid':        '',
                'wifi_pw':          '',
                'ap_pw':            'myobiPassword',
                'tz_offset':        3600,
                'mqtt_enable':      True,
                'mqtt_keepalive':   0,
                'mqtt_cid':         unique_machine_id,
                'mqtt_server':      'iot.eclipse.org',
                'mqtt_user':        '',
                'mqtt_pw':          '',
                'mqtt_subt':        initial_hostname + '/' + 'switch/action',
                'mqtt_pubt':        initial_hostname + '/' + 'switch/status'
}

# ----------------------------------------------------------------------------
