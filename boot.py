# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import uos, machine
uos.dupterm(machine.UART(0, 115200), 1)
import gc
import webrepl

print("\n\nINFO: --- Starting up. ---")
webrepl.start()

gc.collect()
print('INFO: Bytes free after boot: {}'.format(gc.mem_free()))
print("INFO: --- Boot done. ---")
