# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
uos.dupterm(machine.UART(0, 115200), 1)
import gc
import webrepl
import obi_wifi
import port_io
import config as cfg
import network

print("INFO: --- Starting up. ---")
webrepl.start()

print("INFO: Setting up I/O ports:")
port_io.setup_ports()

gc.collect()
print('INFO: Bytes free after boot: {}'.format(gc.mem_free()))
print("INFO: --- Boot done. ---")
