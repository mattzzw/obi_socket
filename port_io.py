from machine import Pin
import config as cfg
import utime


class Button:
    """
    Debounced pin handler
    """
    def __init__(self, pin, callback, trigger=Pin.IRQ_FALLING, min_ago=50):
        self.callback = callback
        self.min_ago = min_ago
        self._next_call = utime.ticks_ms() + self.min_ago
        pin.irq(trigger=trigger, handler=self.debounce_handler)

    def call_callback(self, pin):
        self.callback(pin)

    def debounce_handler(self, pin):
        if utime.ticks_ms() > self._next_call:
            self._next_call = utime.ticks_ms() + self.min_ago
            self.call_callback(pin)
        #else:
        #    print("debounce: %s" % (self._next_call - time.ticks_ms()))

def button_on_off_callback(pin):
    print("INFO: Button (%s) changed to: %r" % (pin, pin.value()))
    # toggle relay on releasing the button
    if pin.value():
        toggle_output(cfg.RELAY)
        s = get_output(cfg.RELAY)
        set_output(cfg.LED_R, s)
    else:
        # check for long_press
        pr_time = utime.ticks_ms()
        while (pin.value() == 0):
            if utime.ticks_ms() > pr_time + 3000:
                print("INFO: Resetting config, rebooting.")
                blink_led(100)
                import machine
                import os
                os.remove("wifi.cfg")
                machine.reset()


def toggle_output(port_id):
    set_output(port_id, not get_output(port_id))

def set_output(port_id, value):
    v = translate_port_level(port_id, value)
    cfg.outputs[port_id]['obj'].value(v)

def get_output(port_id):
    value = cfg.outputs[port_id]['obj'].value()
    v = translate_port_level(port_id, value)
    return v

# translates a logical high = "do something" to physical logic level
def translate_port_level(port_id, value):
    if value == 0:
        if cfg.outputs[port_id]['active'] == 'high':
            v = 0  # high active 0
        else:
            v = 1  # low active 0
    else:
        if cfg.outputs[port_id]['active'] == 'high':
            v = 1 # high active 1
        else:
            v = 0 # low active 1
    return v

def get_ports_status():
    status = dict()
    for port in range (1, len(cfg.outputs) + 1):
        status[port] = get_output(port)
    return status

def setup_ports():
    # set output ports
    for port, pcfg in cfg.outputs.items():
        print("INFO: Setting up GPIO {} on pin {}".format(port, pcfg['pin']))
        if pcfg['active'] == 'high':
            # init high active ports with 0
            pcfg['obj'] = Pin(pcfg['pin'], Pin.OUT, value=0)
        else:
            # init low active ports with 1
            pcfg['obj'] = Pin(pcfg['pin'], Pin.OUT, value=1)

        # setup input port
        # hack to clean pending interrupts
        on_off = Pin(cfg.inputs[cfg.ON_OFF]['pin'], Pin.IN, Pin.PULL_UP)
        button_on_off = Button(pin=on_off, callback=button_on_off_callback)

def blink_led(n):
    for i in range(0,n):
        toggle_output(cfg.LED_R)
        utime.sleep(0.03)

def toggle_each_port():
    for port in range (1, len(cfg.outputs) + 1):
        cfg.outputs[port]['obj'].value(0)
        utime.sleep(0.2)
    for port in range (1, len(cfg.outputs) + 1):
        cfg.outputs[port]['obj'].value(1)
        utime.sleep(0.2)
