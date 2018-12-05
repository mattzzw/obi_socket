import gc
from . import obi_socket
from . import port_io
from . import obi_wifi
from . import obi_mqtt
from . import obi_time


# init main app
print("INFO: Setting up I/O ports:")
port_io.setup_ports()

# start access-point
obi_wifi.start_accesspoint(obi_socket.conf)

# Connect to the world...
wifi_is_connected = obi_wifi.do_connect(obi_socket.conf)
if wifi_is_connected:
    obi_mqtt.init_client(obi_socket.conf)
    obi_mqtt.do_connect(obi_mqtt.mqtt_client, obi_socket.conf)
    obi_time.set_rtc_from_ntp(obi_socket.conf)
else:
    client = None

# Show that we are ready
port_io.blink_led(40)

# Start web app
gc.collect()
print("DEBUG: Before app start: ", gc.mem_free())
obi_socket.app.run(debug=True, port = 80,  host = '0.0.0.0')
