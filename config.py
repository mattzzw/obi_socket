import machine
import ubinascii

hw_configs = ['obi_socket', 'bw-shp2']

#hw_config = 'obi-socket'
hw_config = 'bw-shp2'

# ----------------------------------------------------------------------
if hw_config == 'obi-socket':
    ## OBI socket

    # Ports
    outputs           = {   1: { 'pin':  4, 'active': 'high', 'obj' : ''},  # relay port 1
                            2: { 'pin': 12, 'active': 'high', 'obj' : ''},  # LED green
                            3: { 'pin': 13, 'active': 'high', 'obj' : ''}   # LED red
                            }
    inputs            = {   1: { 'pin':  5, 'pullup': 'True', 'obj': ''}  }  # on/off switch

    # Consts
    RELAY = 1
    LED_G = 2
    LED_R = 3
    ON_OFF = 1

elif hw_config == 'bw-shp2':
    ## BW-SHP2

    # Ports
    outputs           = {   1: { 'pin': 15, 'active': 'high', 'obj' : ''},  # relay port 1
                            2: { 'pin': 2, 'active': 'low', 'obj' : ''},  # LED green
                            3: { 'pin': 0, 'active': 'low', 'obj' : ''}   # LED red
                            }
    inputs            = {   1: { 'pin':  13, 'pullup': 'True', 'obj': ''}, # on/off switch
                            2: { 'pin':  14, 'pullup': 'True', 'obj': ''}, # CF1
                            3: { 'pin':   5, 'pullup': 'True', 'obj': ''}  # CF
                            }
    # Consts
    RELAY = 1
    LED_G = 2
    LED_R = 3
    SEL = 4

    ON_OFF = 1
    CF1 = 2
    CF = 3

# ----------------------------------------------------------------------

unique_machine_id = ubinascii.hexlify(machine.unique_id()).decode()
initial_hostname = "obi-socket-{}".format(unique_machine_id[:6])

initial_cfg = {
                'hostname':         initial_hostname,
                'hw_config':        hw_config,
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
