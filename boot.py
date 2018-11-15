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

port_io.setup_ports()
wifi.do_connect()
webrepl.start()
gc.collect()
