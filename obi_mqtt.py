import ubinascii
from umqtt.robust import MQTTClient
import machine
import config as cfg

def do_connect():
    # Setup MQTT connection
    c = MQTTClient(cfg.mqtt_client_id, cfg.mqtt_server)
    c.set_callback(sub_cb)
    try:
        c.connect()   # FIXME - remember if connection was successful or not
        c.subscribe(cfg.mqtt_sub_topic)
        # setup timer to check for messages every 200ms
        tim = machine.Timer(-1)
        tim.init(period=200, mode=machine.Timer.PERIODIC, callback=lambda t:c.check_msg())
        print("INFO: MQTT: Connected as client {} to {}, subscribed to topic {}".format(
            cfg.mqtt_client_id, cfg.mqtt_server, cfg.mqtt_sub_topic))
    except Exception as e:
        print("ERROR: MQTT: Connection to {} failed: {}.".format(cfg.mqtt_sub_topic, e))

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
    c.publish(cfg.mqtt_pub_topic, ujson.dumps(port_io.get_ports_status()))
