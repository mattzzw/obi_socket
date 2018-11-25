import config as cfg
import port_io
import utime
import network

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    config = cfg.load()

    # wifi configured?
    if config['wifi_ssid'] != '':
        wifi_cfg_exists = True
    else:
        wifi_cfg_exists = False

    if wifi_cfg_exists == True:
        wlan.active(True)
        if not wlan.isconnected():
            print("INFO: Setting client hostname to {}".format(config['hostname']))
            wlan.config(dhcp_hostname=config['hostname'])
            print('INFO: Connecting to network...')
            wlan.connect(config['wifi_ssid'], config['wifi_password'])
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
        wifi_is_connected = False

    return wifi_is_connected
