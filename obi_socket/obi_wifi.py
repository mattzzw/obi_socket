import utime
import network
from . import config as cfg
from . import port_io


def do_connect(config):
    wlan = network.WLAN(network.STA_IF)

    # wifi configured?
    if config[cfg.idx('wifi_ssid')] != '':
        wifi_cfg_exists = True
    else:
        wifi_cfg_exists = False

    if wifi_cfg_exists == True:
        wlan.active(True)
        if not wlan.isconnected():
            print("INFO: Setting client hostname to {}".format(config[cfg.idx('hostname')]))
            wlan.config(dhcp_hostname=config[cfg.idx('hostname')])
            print('INFO: Connecting to network...')
            wlan.connect(config[cfg.idx('wifi_ssid')], config[cfg.idx('wifi_pw')])
            tmo = 0
            while not wlan.isconnected():
                # try to connect and flash green LED
                port_io.set_output(cfg.LED_G, 1)
                utime.sleep_ms(100)
                port_io.set_output(cfg.LED_G, 0)
                utime.sleep_ms(100)
                tmo += 1
                if tmo > 50: # timeout after ~10 seconds
                    wlan.active(False)
                    break
    else:
        # no client config found
        print("INFO: No wifi client config found.")
        wlan.active(False)
        port_io.blink_slowly()

    # timeout or connected?
    if wlan.isconnected():
        print("INFO: Wifi client connected. Stopping access-point.")
        # disable access-point
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(False)
        port_io.set_output(cfg.LED_G, 1)
        print('INFO: Network config:', wlan.ifconfig())
        wifi_is_connected = True
    else:
        # FIXME: if enabled this can lead to a boot loop (timer/mqtt clash?)
        #port_io.blink_slowly()
        wifi_is_connected = False

    return wifi_is_connected

def start_accesspoint(conf):
    print("INFO: --- Setting up AP ---")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    print("INFO: Setting AP name to {}".format(conf[cfg.idx('hostname')]))
    print("INFO: Seeting Pw to {}".format(conf[cfg.idx('ap_pw')]))
    try:
        ap_if.config(essid=conf[cfg.idx('hostname')],
                     authmode=network.AUTH_WPA_WPA2_PSK, \
                     password=conf[cfg.idx('ap_pw')])
    except OSError:
        print("ERROR: Setting up AP failed.")
