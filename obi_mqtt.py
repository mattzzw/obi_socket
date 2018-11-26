from umqtt.robust import MQTTClient
import machine
import port_io
import ujson

def init_client(config):
    client = MQTTClient(config['mqtt_cid'], config['mqtt_server'],
                   user = config['mqtt_user'],
               password = config['mqtt_pw'])
    return client

def do_connect(client, config):
    # Setup MQTT connection
    config['mqtt_con_status'] = ''
    if config['mqtt_enable'] != 0:
        client.set_callback(sub_cb)
        try:
            rc = client.connect()
        except Exception as e:
            print("ERROR: MQTT: Connection to {} failed: {}.".format(config['mqtt_server'], e))
            config['mqtt_connection'] = e
        else:
            client.subscribe(config['mqtt_subt'])
            # setup timer to check for messages every 200ms
            tim = machine.Timer(-1)
            tim.init(period=200, mode=machine.Timer.PERIODIC,
                     callback=lambda t:client.check_msg())
            print("INFO: MQTT: Connected as client {} to {}, subscribed to topic {}".format(
                config['mqtt_cid'], config['mqtt_server'], config['mqtt_subt']))
            config['mqtt_con_status']='Success'
        #cfg.save(config)
    else:
        #cfg.save(config)
        print("INFO: MQTT: Not starting.")


# MQTT callback
def sub_cb(client, config, topic, msg):
    print("INFO: MQTT: Received data: {}".format((topic, msg)))
    if msg == b"on":
        port_io.set_output(1, 1)
        port_io.set_output(3, 1)
    elif msg == b"off":
        port_io.set_output(1, 0)
        port_io.set_output(3, 0)
    elif msg == b"toggle":
        port_io.toggle_output(1)
        port_io.toggle_output(3)
    publish_status(client, config)

def publish_status(client, config):
    port_status = ujson.dumps(port_io.get_ports_status())
    client.publish(config['mqtt_pubt'], port_status)
