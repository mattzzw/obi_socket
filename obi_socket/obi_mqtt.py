from umqtt.robust import MQTTClient
import machine
from . import config as cfg
from . import port_io

mqtt_con_status = 'Not connected'
mqtt_client = None

def init_client(config):
    global mqtt_client
    mqtt_client = MQTTClient(config['mqtt_cid'], config['mqtt_server'],
                   user = config['mqtt_user'],
               password = config['mqtt_pw'],
               keepalive = int(config['mqtt_keepalive']))
    return mqtt_client

def do_connect(client, config):
    # Setup MQTT connection
    global mqtt_con_status
    if config['mqtt_enable'] == 'True':
        client.set_callback(sub_cb)
        try:
            rc = client.connect()
        except Exception as e:
            print("ERROR: MQTT: Connection to {} failed: {}.".format(config['mqtt_server'], e))
            mqtt_con_status = e
        else:
            client.subscribe(config['mqtt_subt'])
            # setup timer to check for messages every 200ms
            tim = machine.Timer(-1)
            tim.init(period = 200, mode = machine.Timer.PERIODIC,
                     callback = lambda t:client.check_msg())
            print("INFO: MQTT: Connected as client {} to {}, subscribed to topic {}".format(
                config['mqtt_cid'], config['mqtt_server'], config['mqtt_subt']))
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
    if config['mqtt_enable'] == 'True':
        client.publish(config['mqtt_pubt'], msg)
        print("INFO: MQTT: Published data to {}: {}".format(config['mqtt_pubt'], msg))
