import machine
import picoweb
import ujson
import config as cfg
import port_io
import time
import os
import gc

app = picoweb.WebApp("myApp")

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
    machine.reset()
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Done.")

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
    status = port_io.get_ports_status()
    yield from picoweb.start_response(resp, content_type = "application/json")
    yield from resp.awrite(ujson.dumps(status))

@app.route('/toggle')
def toggle(req, resp):
    queryString = req.qs
    parameters = qs_parse(queryString)
    for key, val in parameters.items():
        if key == 'pwr':
            print("INFO: toggling power for {} seconds".format(key, val))
            port_io.toggle_output(cfg.RELAY)
            port_io.toggle_output(cfg.LED_R)
            if float(val) > 0:
                time.sleep(float(val))
                port_io.toggle_output(cfg.RELAY)
                port_io.toggle_output(cfg.LED_R)
    status = port_io.get_ports_status()
    yield from picoweb.start_response(resp, content_type = "application/json")
    yield from resp.awrite(ujson.dumps(status))

@app.route("/")
def index(req, resp):
    method = req.method
    print("Method was:" + method)
    if method == "POST":
        yield from picoweb.start_response(resp)
        yield from resp.awrite("POST method incoming")
    else:
        import network
        yield from picoweb.start_response(resp)
        wlan = network.WLAN(network.STA_IF)
        yield from resp.awrite("<html><head><style TYPE=\"text/css\">html {font-family: sans-serif;}</style></head><body>")
        yield from resp.awrite("<h1>Hi, this is {}</h1>".format(os.uname()[0]))
        yield from resp.awrite("<pre>Wifi interface: {} <br />".format(wlan.ifconfig()))
        yield from resp.awrite("Firmware version: {} <br />".format(os.uname()[3]))
        yield from resp.awrite("{} bytes free<br />".format(gc.mem_free()))
        status = port_io.get_ports_status()
        yield from resp.awrite("Port status: {}</pre>".format(ujson.dumps(status)))
        yield from resp.awrite("<a href=\"/setup\">Wifi Setup</a>")
        yield from resp.awrite("<hr />Power is")
        if port_io.get_output(cfg.RELAY) == 1:
            yield from resp.awrite("<h2>ON</h2>")
        else:
            yield from resp.awrite("<h2>OFF</h2>")
        yield from resp.awrite("<a href=\"/toggle?pwr=0\">Toggle</a><br />")
        yield from resp.awrite("</body></html>")

@app.route('/setup')
def setup(req, resp):
    method = req.method
    print("Method was:" + method)
    if method == "POST":
        yield from req.read_form_data()
        if req.form.get('ssid'):
            ssid = req.form['ssid'][0]
            password = req.form['password'][0]
            yield from picoweb.start_response(resp)
            yield from resp.awrite("<html><head><style TYPE=\"text/css\">html {font-family: sans-serif;}</style></head><body>")
            yield from resp.awrite("Saved config.<br />")
            yield from resp.awrite("<a href=\"/reset\">Reboot</a> to connect to wifi {}".format(ssid))
            wifi_config = open("wifi.cfg", 'w')
            wifi_config.write(ssid)
            wifi_config.write('\n')
            wifi_config.write(password)
            wifi_config.close()
    else:
        yield from picoweb.start_response(resp)
        yield from resp.awrite("<html><head><style TYPE=\"text/css\">html {font-family: sans-serif;}</style></head><body>")
        yield from resp.awrite("""
<form id=\"wifi_config\" method=\"post\">
<table><tr>
<td>SSID:</td>
<td><input name=\"ssid\" type=\"text\" ></td></tr>
<tr>
<td>Password:</td>
<td><input name=\"password\" type=\"password\"></td></tr>
<tr>
<td></td><td><input type=\"submit\" value=\"Save\"></td></tr>
</table>
</form>
""")
        yield from resp.awrite("</body></html>")


port_io.blink_led()
app.run(debug=True, port = 80,  host = '0.0.0.0')
