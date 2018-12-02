from umqtt.robust import MQTTClient
import machine
import ujson
from . import config as cfg
from . import port_io

mqtt_con_status = 'Not connected'

def init_client(config):
    client = MQTTClient(config[cfg.idx('mqtt_cid')],
                        config[cfg.idx('mqtt_server')],
                   user = config[cfg.idx('mqtt_user')],
               password = config[cfg.idx('mqtt_pw')],
               keepalive = int(config[cfg.idx('mqtt_kalive')]))
    return client

def do_connect(client, config):
    # Setup MQTT connection
    global mqtt_con_status
    if config[cfg.idx('mqtt_enable')] == 'True':
        client.set_callback(sub_cb)
        try:
            rc = client.connect()
        except Exception as e:
            print("ERROR: MQTT: Connection to {} failed: {}.".format(config[cfg.idx('mqtt_server')], e))
            mqtt_con_status = e
        else:
            client.subscribe(config[cfg.idx('mqtt_subt')])
            # setup timer to check for messages every 200ms
            tim = machine.Timer(-1)
            tim.init(period = 200, mode = machine.Timer.PERIODIC,
                     callback = lambda t:client.check_msg())
            print("INFO: MQTT: Connected as client {} to {}, subscribed to topic {}".format(
                config[cfg.idx('mqtt_cid')], config[cfg.idx('mqtt_server')], config[cfg.idx('mqtt_subt')]))
            mqtt_con_status='Success'
    else:
        print("INFO: MQTT: Not enabled, not starting.")

# MQTT callback
def sub_cb(topic, msg):
    print("INFO: MQTT: Received data: {}".format((topic, msg)))
    if msg == b"on":
        port_io.set_output(cfg.RELAY, 1)
        port_io.set_output(cfg.LED_R, 1)
    elif msg == b"off":
        port_io.set_output(cfg.RELAY, 0)
        port_io.set_output(cfg.LED_R, 0)
    elif msg == b"toggle":
        port_io.toggle_output(cfg.RELAY)
        port_io.toggle_output(cfg.LED_R)
    # FIXME how to publish mqtt status in callback routing?
    # Can't config/client parameters

def publish_status(client, config, msg):
    if config[cfg.idx('mqtt_enable')] == 'True':
        client.publish(config[cfg.idx('mqtt_pubt')], msg)
        print("INFO: MQTT: Published data to {}: {}".format(config[cfg.idx('mqtt_pubt')], msg))
