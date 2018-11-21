import config as cfg
import port_io
import utime
import ubinascii
import network
import ujson

def get_wifi_cfg():
    try:
        f = open("wifi.cfg")
        p = f.read()
        f.close()
    except:
        p = '{}'
    return ujson.loads(p)

def get_hostname_ssid():
    wlan = network.WLAN(network.STA_IF)
    wifi_cfg = get_wifi_cfg()
    if len(wifi_cfg) == 0:
        mac = ubinascii.hexlify(wlan.config('mac')).decode()
        hostname = "obi-socket-{}".format(mac[-6:])
        ssid = "not configured"
    else:
        hostname = wifi_cfg['hostname']
        ssid = wifi_cfg['ssid']
    return (hostname, ssid)


def do_connect():

    wlan = network.WLAN(network.STA_IF)

    cfg_dict = get_wifi_cfg()
    try:
        ssid = cfg_dict['ssid']
        pw = cfg_dict['pw']
        hostname = cfg_dict['hostname']
        wifi_cfg_exists = True
    except:
        wifi_cfg_exists = False


    if wifi_cfg_exists == True:
        wlan.active(True)
        if not wlan.isconnected():
            print("INFO: Setting client hostname to {}".format(hostname))
            wlan.config(dhcp_hostname=hostname)
            print('INFO: Connecting to network...')
            wlan.connect(ssid, pw)
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
