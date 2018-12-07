import machine
import utime
import ntptime
from . import config as cfg

rtc = machine.RTC()

def set_rtc_from_ntp(config):
    try:
        mytime = utime.localtime(ntptime.time() + int(config[cfg.idx('tz_offset')]))
    except:
        mytime = utime.localtime()
    year, month, day, hour, minute, second, weekday, yearday = mytime
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
    print("INFO: Set RTC to {}-{}-{} {:02}:{:02}:{:02}"
          .format(year, month, day, hour, minute, second))
