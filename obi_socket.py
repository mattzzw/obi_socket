import machine
import picoweb
import ujson
import config as cfg
import port_io
import wifi
import utime
import uos
import gc
import ubinascii

app = picoweb.WebApp("myApp")

html_header = "<html><head><style TYPE=\"text/css\">html \
    {font-family: sans-serif;}</style></head><body>"
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
    # redirect to "/"
    headers = {"Location": "/"}
    yield from picoweb.start_response(resp, status="303", headers=headers)

@app.route('/toggle')
def toggle(req, resp):
    queryString = req.qs
    parameters = qs_parse(queryString)
    for key, val in parameters.items():
        if key == 'pwr':
            print("INFO: toggling power for {} seconds".format(val))
            port_io.toggle_output(cfg.RELAY)
            port_io.toggle_output(cfg.LED_R)
            if float(val) > 0:
                utime.sleep(float(val))
                port_io.toggle_output(cfg.RELAY)
                port_io.toggle_output(cfg.LED_R)
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
        import network
        wlan = network.WLAN(network.STA_IF)
        status = port_io.get_ports_status()
        wifi_cfg = wifi.get_wifi_cfg()
        if len(wifi_cfg) == 0:
            mac = ubinascii.hexlify(wlan.config('mac')).decode()
            hostname = "obi-socket-{}".format(mac[-6:])
            ssid = "not configured"
        else:
            hostname = wifi_cfg['hostname']
            ssid = wifi_cfg['ssid']
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("<h1>Hi, this is {}</h1>".format(hostname))
        yield from resp.awrite("<pre>")
        yield from resp.awrite("Wifi interface   : {} <br />".format(wlan.ifconfig()))
        yield from resp.awrite("Configured SSID  : {} <br />".format(ssid))
        yield from resp.awrite("Firmware version : {} <br />".format(uos.uname()[3]))
        yield from resp.awrite("Bytes free       : {} <br />".format(gc.mem_free()))
        yield from resp.awrite("Port status      : {}</pre>".format(ujson.dumps(status)))
        yield from resp.awrite("<a href=\"/setup\">Wifi Setup</a>")
        yield from resp.awrite("<hr />Power is")
        if port_io.get_output(cfg.RELAY) == 1:
            yield from resp.awrite("<h2>ON</h2>")
        else:
            yield from resp.awrite("<h2>OFF</h2>")
        yield from resp.awrite("<a href=\"/toggle?pwr=0\">Toggle</a><br />")
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


wifi.do_connect()
port_io.blink_led(20)
app.run(debug=True, port = 80,  host = '0.0.0.0')
