import machine
import ubinascii

hw_configs = ['obi_socket', 'bw-shp2']

hw_config = 'obi-socket'
#hw_config = 'bw-shp2'

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
                            2: { 'pin': 2,  'active': 'low',  'obj' : ''},  # LED blue
                            3: { 'pin': 0,  'active': 'low',  'obj' : ''},   # LED red
                            4: { 'pin': 12, 'active': 'high', 'obj' : ''}   # SEL pin

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


# using a list to store config information (dicts take too much memory)

# list indeces/keys:

keys = ['hostname',
        'wifi_ssid',
        'wifi_pw',
        'hw_config',
        'ap_pw',
        'tz_offset',
        'mqtt_enable',
        'mqtt_kalive',
        'mqtt_server',
        'mqtt_user',
        'mqtt_pw',
        'mqtt_cid',
        'mqtt_subt',
        'mqtt_pubt'
        ]

initial_cfg = [
                initial_hostname,                           # hostname
                '',                                         # wifi_ssid
                '',                                         # wifi_pw
                hw_config,                                  # hw_config
                'myobiPassword',                            # ap_pw
                3600,                                       # tz_offset
                True,                                       # mqtt_enable
                0,                                          # mqtt_kalive
                'iot.eclipse.org',                          # mqtt_server
                '',                                         # mqtt_user
                '',                                         # mqtt_pw
                unique_machine_id,                          # mqtt_cid
                initial_hostname + '/' + 'switch/action',   # mqtt_subt
                initial_hostname + '/' + 'switch/status'    # mqtt_pubt
]

# cfg.idx(key) is a bit more readable than cfg.keys.index(key)
def idx(key):
    global keys
    # return the index of the key string
    return keys.index(key)

# ----------------------------------------------------------------------------
