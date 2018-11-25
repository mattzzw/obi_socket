# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
uos.dupterm(machine.UART(0, 115200), 1)
import gc
import webrepl
import wifi
import port_io
import config as cfg
import network

print("INFO: --- Starting up. ---")
webrepl.start()

print("INFO: Setting up I/O ports:")
port_io.setup_ports()

# start access-point to be sure
print("INFO: --- Setting up AP ---")
config = cfg.load()
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
print("INFO: Setting AP name to {}".format(config['hostname']))
print("INFO: Seeting Pw to {}".format(config['ap_password']))
try:
    ap_if.config(essid=config['hostname'], authmode=network.AUTH_WPA_WPA2_PSK, \
                 password=config['ap_password'])
except OSError:
    print("ERROR: Setting up AP failed.")
gc.collect()
print("INFO: --- Boot done. ---")
