from umqtt.robust import MQTTClient
import machine
import config as cfg
import port_io
import ujson

config = cfg.load()
c = MQTTClient(config['mqtt_client_id'], config['mqtt_server'],
               user = config['mqtt_user'],
           password = config['mqtt_password'])

def do_connect():
    # Setup MQTT connection
    config = cfg.load()
    config['mqtt_con_status'] = ''
    if config['mqtt_enable'] == True:
        c.set_callback(sub_cb)
        try:
            rc = c.connect()
        except Exception as e:
            print("ERROR: MQTT: Connection to {} failed: {}.".format(config['mqtt_server'], e))
            config['mqtt_connection'] = e
        else:
            c.subscribe(config['mqtt_sub_topic'])
            # setup timer to check for messages every 200ms
            tim = machine.Timer(-1)
            tim.init(period=200, mode=machine.Timer.PERIODIC,
                     callback=lambda t:c.check_msg())
            print("INFO: MQTT: Connected as client {} to {}, subscribed to topic {}".format(
                config['mqtt_client_id'], config['mqtt_server'], config['mqtt_sub_topic']))
            config['mqtt_connection']='Success'
        cfg.save(config)
    else:
        cfg.save(config)

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
    publish_status()

def publish_status():
    port_status = ujson.dumps(port_io.get_ports_status())
    c.publish(config['mqtt_pub_topic'], port_status)
