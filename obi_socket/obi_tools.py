import machine
import ubinascii
import ujson
import uos
import gc
from . import config as cfg

gc.collect()
#buf = bytearray(512)

def load_cfg():
    gc.collect()
    # check if this is 1st time configuration
    try:
        f = open("obi_socket.cfg")
    except:
        # first time
        cfg_list = cfg.initial_cfg
        dump_cfg(cfg_list)
    else:
        buf = f.read()
        f.close()

        try:
            cfg_list = ujson.loads(buf)
        except Exception as e:
            clear_cfg()
            machine.reset()
        else:
            #dump_cfg(cfg_list)
            gc.collect()
    return cfg_list

def save_cfg(cfg_list):
    gc.collect()
    #dump_cfg(cfg_dict)
    f = open("obi_socket.cfg", 'w')
    ujson.dump(cfg_list, f)
    f.close()
    gc.collect()

def clear_cfg():
    try:
        uos.remove("obi_socket.cfg")
    except:
        pass
    else:
        pass

def dump_cfg(cfg_list):
    k = 0
    for v in cfg_list:
        k += 1
