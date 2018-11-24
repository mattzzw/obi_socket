import machine
import picoweb
import ujson
import config as cfg    # local module
import port_io          # local module
import wifi             # local module
import obi_mqtt         # local module
import utime
import uos
import gc
import ubinascii
import ntptime


app = picoweb.WebApp(None)

html_header = '''<!DOCTYPE html>
<html>
<head>
<title>obi-socket</title>
<link rel="stylesheet" href="/static/mini-default.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<header class="sticky row">
  <div class="col-sm col-md-10 col-md-offset-1">
    <a href="/" role="button">Home</a>
    <a href="/setup" role="button">Setup</a>
    <a href="/system" role="button">System</a>
  </div>
</header>
<br />
<div class="container">
  <div class="row cols-sm-12 cols-md-10" >
    <div class="col-md-offset-1" >
'''
html_wifi_form = "Enter wifi client config:</br> \
    <form id=\"wifi_config\" method=\"post\"> \
    <table><tr> \
    <td>SSID:</td> \
    <td><input name=\"ssid\" type=\"text\" ></td></tr> \
    <tr> \
    <td>Password:</td> \
    <td><input name=\"password\" type=\"password\"></td></tr> \
    <tr> \
    <td>Hostname:</td> \
    <td><input name=\"hostname\" type=\"text\" value=\"obi-socket\"></td></tr> \
    <tr> \
    <td></td><td><input type=\"submit\" value=\"Save\"></td></tr> \
    </table> \
    </form>"



def qs_parse(qs):
    parameters = {}
    ampersandSplit = qs.split("&")
    for element in ampersandSplit:
        equalSplit = element.split("=")
        parameters[equalSplit[0]] = equalSplit[1]
    return parameters

@app.route('/debug')
def debug_action(req, resp):
    port_io.toggle_each_port()
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Done.")

@app.route('/reset')
def reset_socket(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Done.")
    machine.reset()

@app.route('/status')
def get_status(req, resp):
    status = port_io.get_ports_status()
    yield from picoweb.start_response(resp, content_type = "application/json")
    yield from resp.awrite(ujson.dumps(status))

@app.route('/switch')
def switch(req, resp):
    queryString = req.qs
    parameters = qs_parse(queryString)
    for key, val in parameters.items():
        if key == 'pwr':
            if val in ('on', 'off'):
                print("INFO: switching power to {}".format(key, val))
                if val == 'on':
                    port_io.set_output(cfg.RELAY, 1)
                    port_io.set_output(cfg.LED_R, 1)
                elif val == 'off':
                    port_io.set_output(cfg.RELAY, 0)
                    port_io.set_output(cfg.LED_R, 0)
                obi_mqtt.publish_status()

    # redirect to "/"
    headers = {"Location": "/"}
    yield from picoweb.start_response(resp, status="303", headers=headers)

@app.route('/toggle')
def toggle(req, resp):
    queryString = req.qs
    parameters = qs_parse(queryString)
    for key, val in parameters.items():
        if key == 'duration':
            print("INFO: toggling power for {} seconds".format(val))
            port_io.toggle_output(cfg.RELAY)
            port_io.toggle_output(cfg.LED_R)
            obi_mqtt.publish_status()
            if float(val) > 0:
                utime.sleep(float(val))
                port_io.toggle_output(cfg.RELAY)
                port_io.toggle_output(cfg.LED_R)
                obi_mqtt.publish_status()
    # redirect to "/"
    headers = {"Location": "/"}
    yield from picoweb.start_response(resp, status="303", headers=headers)

@app.route("/")
def index(req, resp):
    method = req.method
    if method == "POST":
        pass
    else:
        # GET
        (hostname, ssid) = wifi.get_hostname_ssid()
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("<h1>Hi, this is {}</h1>".format(hostname))
        yield from resp.awrite("<hr />Power is")
        if port_io.get_output(cfg.RELAY) == 1:
            yield from resp.awrite("<h2>ON</h2>")
        else:
            yield from resp.awrite("<h2>OFF</h2>")
        yield from resp.awrite("<a href=\"/toggle?pwr=0\">Toggle</a><br />")
        yield from resp.awrite("</body></html>")
        gc.collect()

@app.route('/system')
def system(req, resp):
    method = req.method
    if method == "POST":
        pass
    else:
        # GET
        import network
        wlan = network.WLAN(network.STA_IF)
        (hostname, ssid) = wifi.get_hostname_ssid()
        status = port_io.get_ports_status()
        try:
            mytime = utime.localtime(ntptime.time())
        except:
            mytime = utime.localtime()
        year, month, day, hour, minute, second, ms, dayinyear = mytime
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("<h1>{} - System Info</h1>".format(hostname))
        yield from resp.awrite("<p><table style=\"max-height:800px\"><thead><th>Item</th><th>Config</th></thead>")
        yield from resp.awrite("<tr><td>Wifi interface</td><td><code>{}</code></td></tr>".format(wlan.ifconfig()))
        yield from resp.awrite("<tr><td>Configured SSID</td><td><code>{}</code></td></tr>".format(ssid))
        yield from resp.awrite("<tr><td>MQTT initial status</td><td><code>{}</code></td></tr>".format(mqtt_is_connected))
        yield from resp.awrite("<tr><td>MQTT server</td><td><code>{}</code></td></tr>".format(cfg.mqtt_server))
        yield from resp.awrite("<tr><td>MQTT sub topic</td><td><code>{}</code></td></tr>".format(cfg.mqtt_sub_topic))
        yield from resp.awrite("<tr><td>MQTT pub topic</td><td><code>{}</code></td></tr>".format(cfg.mqtt_pub_topic))
        yield from resp.awrite("<tr><td>Firmware version</td><td><code>{}</code></td></tr>".format(uos.uname()[3]))
        yield from resp.awrite("<tr><td>Bytes free</td><td><code>{}</code></td></tr>".format(gc.mem_free()))
        yield from resp.awrite("<tr><td>Port status</td><td><code>{}</code></td></tr>".format(ujson.dumps(status)))
        yield from resp.awrite("<tr><td>Time</td><td><code>{}-{}-{} {}:{}</code></td></tr>".format(year, month, day, hour, second))
        yield from resp.awrite("</table><p>")
        yield from resp.awrite("<a href=\"/reset\">Reboot</a>")
        yield from resp.awrite("</body></html>")
        gc.collect()

@app.route('/setup')
def setup(req, resp):
    method = req.method
    if method == "POST":
        yield from req.read_form_data()
        if req.form.get('ssid'):
            ssid = req.form['ssid'][0]
            password = req.form['password'][0]
            hostname = req.form['hostname'][0]
            cfg_dict = dict()
            cfg_dict['ssid'] = ssid
            cfg_dict['pw'] = password
            cfg_dict['hostname'] = hostname

            yield from picoweb.start_response(resp)
            yield from resp.awrite(html_header)
            yield from resp.awrite("Saved config.<br />")
            yield from resp.awrite("<a href=\"/reset\">Reboot</a> to connect to wifi {}".format(ssid))
            wifi_config = open("wifi.cfg", 'w')
            wifi_config.write(ujson.dumps(cfg_dict))
            wifi_config.close()
    else:
        # GET - show form
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite(html_wifi_form)
        yield from resp.awrite("</body></html>")


# FIXME refactor/build a package in sub dir

# Connect to the world...
wifi_is_connected = wifi.do_connect()
if wifi_is_connected:
    mqtt_is_connected = obi_mqtt.do_connect()
else:
    mqtt_is_connected = -1

# Show that we are ready
port_io.blink_led(40)
# Start web app
app.run(debug=True, port = 80,  host = '0.0.0.0')
