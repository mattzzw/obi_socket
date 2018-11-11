import config as cfg
import port_io
import utime

def do_connect():
    if cfg.enable_wifi_client == True:
        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(cfg.ssid, cfg.pw)
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
            port_io.set_output(cfg.LED_G, 1)
            print('network config:', wlan.ifconfig())
