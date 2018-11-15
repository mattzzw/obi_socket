import config as cfg
import port_io
import utime

def do_connect():
    try:
        f = open("wifi.cfg")
        p = f.read()
        s = p.split()
        ssid = s[0]
        pw = s[1]
        f.close()
        wifi_cfg_exists = True
    except OSError:
        wifi_cfg_exists = False
        ssid = ''
        pw = ''

    if wifi_cfg_exists == True:
        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        if not wlan.isconnected():
            print('connecting to network...')
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
        # timeout or connected?
        if wlan.isconnected():
            # disable access-point
            ap_if = network.WLAN(network.AP_IF)
            ap_if.active(False)
            port_io.set_output(cfg.LED_G, 1)
            print('network config:', wlan.ifconfig())
