from machine import Pin
import config as cfg
import time

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

def board_init():
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
    on_off = Pin(cfg.inputs[cfg.ON_OFF]['pin'], Pin.IN, Pin.PULL_UP)
    on_off.irq(trigger = Pin.IRQ_FALLING, handler = toggle_on_off)

def toggle_on_off(p):
    # hack to disable interrupts
    on_off = Pin(cfg.inputs[cfg.ON_OFF]['pin'], Pin.IN, Pin.PULL_UP)
    on_off.irq(trigger = 0, handler = toggle_on_off)
    print("INFO: Button pressed:", p)
    toggle_output(cfg.RELAY)
    s = get_output(cfg.RELAY)
    set_output(cfg.LED_R, s)

    # debounce time
    time.sleep(0.5)
    on_off.irq(trigger = Pin.IRQ_FALLING, handler = toggle_on_off)


def blink_led():
    for i in range(0,20):
        toggle_output(cfg.LED_R)
        time.sleep(0.03)

def toggle_each_port():
    for port in range (1, len(cfg.outputs) + 1):
        cfg.outputs[port]['obj'].value(0)
        time.sleep(0.2)
    for port in range (1, len(cfg.outputs) + 1):
        cfg.outputs[port]['obj'].value(1)
        time.sleep(0.2)
