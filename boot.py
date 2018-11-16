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
import ubinascii

port_io.setup_ports()

# start access-point to be sure
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
mac = ubinascii.hexlify(ap_if.config('mac')).decode()
ap_name = "obi_socket-{}".format(mac[:4])
print("Setting AP name to {}".format(ap_name))
ap_if.config(essid=ap_name, authmode=network.AUTH_WPA_WPA2_PSK, password="myobisocket")
webrepl.start()
gc.collect()
print("--- Boot done. ---")
