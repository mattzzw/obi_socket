import machine
import utime
import ntptime
from . import config as cfg

rtc = machine.RTC()

boot_time = None

def set_rtc_from_ntp(config):
    global boot_time
    try:
        mytime = utime.localtime(ntptime.time() + int(config[cfg.idx('tz_offset')]))
    except:
        mytime = utime.localtime()
    boot_time = mytime
    year, month, day, hour, minute, second, weekday, yearday = mytime
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
