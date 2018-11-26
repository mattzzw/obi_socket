import machine
import ubinascii
import ujson
import uos
import gc

gc.collect()
buf = bytearray(512)

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

def load():
    gc.collect()
    print("DEBUG: Before load: ", gc.mem_free())
    # check if this is 1st time configuration
    try:
        f = open("obi_socket.cfg")
    except:
        # first time
        print('INFO: No config found, using initial config.')
        cfg_dict = initial_cfg
    else:
        buf = f.read()
        f.close()
        cfg_dict = ujson.loads(buf)
    print('INFO: Loading cfg')
    #dump_cfg(cfg_dict)
    gc.collect()
    print("DEBUG: After load: ", gc.mem_free())
    return cfg_dict

def save():
    gc.collect()
    print("DEBUG: Before save: ", gc.mem_free())
    print('INFO: Saving cfg')
    #dump_cfg(cfg_dict)
    f = open("obi_socket.cfg", 'w')
    ujson.dump(buf, f)
    f.close()
    gc.collect()
    print("DEBUG: After  save: ", gc.mem_free())

def clear():
    try:
        uos.remove("obi_socket.cfg")
    except:
        pass
    else:
        print('INFO: Cleared/deleted config.')

def dump_cfg(cfg):
    for k, v in sorted(cfg.items()):
        print('INFO: CFG: {:<15}: {:<20}'.format(k, v))
