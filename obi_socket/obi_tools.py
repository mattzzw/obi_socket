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
    print("DEBUG: Before load: ", gc.mem_free())
    # check if this is 1st time configuration
    try:
        f = open("obi_socket.cfg")
    except:
        # first time
        print('INFO: No config found, using initial config.')
        cfg_list = cfg.initial_cfg
        dump_cfg(cfg_list)
    else:
        buf = f.read()
        f.close()

        try:
            cfg_list = ujson.loads(buf)
        except Exception as e:
            print("ERROR: Reading JSON: {}".format(e))
            print('INFO: Deleting config, restarting.')
            clear_cfg()
            machine.reset()
        else:
            print('INFO: Loading cfg')
            #dump_cfg(cfg_list)
            gc.collect()
            print("DEBUG: After load: ", gc.mem_free())
    return cfg_list

def save_cfg(cfg_list):
    gc.collect()
    print("DEBUG: Before save: ", gc.mem_free())
    print('INFO: Saving cfg')
    #dump_cfg(cfg_dict)
    f = open("obi_socket.cfg", 'w')
    ujson.dump(cfg_list, f)
    f.close()
    gc.collect()
    print("DEBUG: After  save: ", gc.mem_free())

def clear_cfg():
    try:
        uos.remove("obi_socket.cfg")
    except:
        pass
    else:
        print('INFO: Cleared/deleted config.')

def dump_cfg(cfg_list):
    k = 0
    for v in cfg_list:
        print('INFO: CFG: {:<15}: {:<20}'.format(cfg.keys[k], v))
        k += 1
