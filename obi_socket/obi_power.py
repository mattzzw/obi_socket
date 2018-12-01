import utime
from machine import Pin, Timer
from . import config as cfg
from . import port_io

cf1_count = 0
cf_count = 0
cf1_frequency = 0
cf_frequency = 0
sel = 0

'''
Upstream/Downstream values of voltage devider:

Ru/Rd = 2400/1

Series resistor for current measurement:

Rs = 0.001

From the data sheet:

Vref = 1.218

Power:
FCF = 1721506  * V(V)*V(I) / Vref^2

Voltage:
FCFU = 15397 *  V(V) / Vref

Current:
FCFI = 94638 *  V(I) / Vref
'''

def calc_power(cf, cf1, sel):
    if sel:
        v = cf1 * 0.18677
        i = 0.0
    else:
        v = 0.0
        i = cf1 * 0.01287
    p = cf * 2.069
    return v, i, p

def callback_cf1(p):
    global cf1_count
    cf1_count += 1

def callback_cf(p):
    global cf_count
    cf_count += 1

def total(t):
    global cf_count
    global cf1_count
    global sel
    cf1_frequency = cf1_count
    cf_frequency = cf_count
    cf1_count = 0
    cf_count = 0
    print("--> ",sel, calc_power(cf_frequency, cf1_frequency, sel))

port_io.setup_ports()

port_io.set_output(cfg.RELAY, 1)
port_io.set_output(cfg.LED_R, 1)

cf1_pin = cfg.inputs[cfg.CF1]['obj']
cf_pin = cfg.inputs[cfg.CF]['obj']

print(cf1_pin, cf_pin)

cf1_pin.irq(trigger=Pin.IRQ_FALLING, handler=callback_cf1)
cf_pin.irq(trigger=Pin.IRQ_FALLING, handler=callback_cf)


# IRQ method
'''
timer = Timer(-1)
timer.init(period=1000, mode=Timer.PERIODIC, callback=total)

while (1):
    port_io.set_output(cfg.SEL, sel)
    port_io.set_output(cfg.LED_G, sel)
    utime.sleep(5)
    sel = 1 - sel # toggle
'''

# polling method
while(1):
    port_io.set_output(cfg.SEL, sel)
    port_io.set_output(cfg.LED_G, sel)

    cf1_count = 0
    cf_count = 0
    utime.sleep(1)
    cf1_frequency = cf1_count
    cf_frequency = cf_count
    print("--> ",sel, calc_power(cf_frequency, cf1_frequency, sel))

    sel = 1 - sel # toggle
