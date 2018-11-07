import config as cfg
import port_io

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(cfg.ssid, cfg.pw)
        while not wlan.isconnected():
            pass
    port_io.set_output(cfg.LED_G, 1)
    print('network config:', wlan.ifconfig())
