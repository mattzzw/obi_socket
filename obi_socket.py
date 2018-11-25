import machine
import picoweb
import ujson
import config as cfg    # local module
import port_io          # local module
import wifi             # local module
import obi_mqtt         # local module
#import obi_html         # local module
import utime
import uos
import gc
import ubinascii
import ntptime
import uasyncio as asyncio


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
    <a href="/info" role="button">System Info</a>
  </div>
</header>
<br />
<div class="container">
  <div class="row cols-sm-12 cols-md-10" >
    <div class="col-md-offset-1" >
'''

html_wifi_form = '''Enter wifi client config:</br>
    <form id="wifi_config" method="post">
    <table><tr>
    <td>SSID:</td>
    <td><input name="ssid" type="text" ></td></tr>
    <tr>
    <td>Password:</td>
    <td><input name="password" type="password"></td></tr>
    <tr>
    <td>Hostname:</td>
    <td><input name="hostname" type="text" value="obi-socket"></td></tr>
    <tr>
    <td></td><td><input type="submit" value="Save"></td></tr>
    </table>
    </form>
    '''
html_action = '''<p>
    <a href="http://obi-socket/toggle?duration=0">
	<button class="primary large"><span class="icon-settings inverse"></span>
	Toggle</button></a>
'''


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
                print("INFO: switching power to {}".format(val))
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
        config = cfg.load()
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("<h1>Hi, this is {}</h1>".format(config['hostname']))
        yield from resp.awrite("<hr />Power is")
        if port_io.get_output(cfg.RELAY) == 1:
            yield from resp.awrite("<h2>ON</h2>")
        else:
            yield from resp.awrite("<h2>OFF</h2>")
        yield from resp.awrite(html_action)
        yield from resp.awrite("</div></div></div></body></html>")
        gc.collect()

@app.route('/info')
def system(req, resp):
    method = req.method
    if method == "POST":
        pass
    else:
        # GET
        import network
        wlan = network.WLAN(network.STA_IF)
        config = cfg.load()
        status = port_io.get_ports_status()
        try:
            mytime = utime.localtime(ntptime.time() + cfg.tz_offset)
        except:
            mytime = utime.localtime()
        year, month, day, hour, minute, second, ms, dayinyear = mytime
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("<h1>{} - System Info</h1>".format(config['hostname']))
        yield from resp.awrite("<p><table style=\"max-height:800px\"><thead><th>Item</th><th>Config</th></thead>")
        for k,v in sorted(config.items()):
            if k != "wifi_password":
                yield from resp.awrite("<tr><td>{}</td><td><code>{}</code></td></tr>".format(k, v))
        yield from resp.awrite("<tr><td>Firmware version</td><td><code>{}</code></td></tr>".format(uos.uname()[3]))
        yield from resp.awrite("<tr><td>Bytes free</td><td><code>{}</code></td></tr>".format(gc.mem_free()))
        yield from resp.awrite("<tr><td>Port status</td><td><code>{}</code></td></tr>".format(ujson.dumps(status)))
        yield from resp.awrite("<tr><td>Time</td><td><code>{}-{}-{} {:02}:{:02}:{:02}</code></td></tr>".format(year, month, day, hour, minute, second))
        yield from resp.awrite("</table><p>")
        yield from resp.awrite('<form action="/restart" method="post"><button name="restart" value="restart">Restart</button></form>')
        yield from resp.awrite('<form action="/reset" method="post"><button name="reset" value="reset">Reset defaults</button></form>')
        yield from resp.awrite("</body></html>")
        gc.collect()


@app.route('/restart')
def reset_socket(req, resp):
    method=req.method
    if method == 'POST':
        # redirect to "/info"
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("Restarting...<br />")
        await asyncio.sleep(3)
        machine.reset()

@app.route('/reset')
def reset_defaults(req, resp):
    method=req.method
    if method == 'POST':
        cfg.clear()
        yield from picoweb.start_response(resp)
        yield from resp.awrite(html_header)
        yield from resp.awrite("Deleted config.<br />")
        yield from resp.awrite("<a href=\"/setup\">Setup</a> a wifi connection")
        yield from resp.awrite("</body></html>")


@app.route('/setup')
def setup(req, resp):
    method = req.method
    if method == "POST":
        cfg_dict = cfg.load()
        yield from req.read_form_data()
        if req.form.get('ssid'):
            ssid = req.form['ssid'][0]
            password = req.form['password'][0]
            hostname = req.form['hostname'][0]
            cfg_dict['wifi_ssid'] = ssid
            cfg_dict['wifi_password'] = password
            cfg_dict['hostname'] = hostname
            cfg.save(cfg_dict)
            yield from picoweb.start_response(resp)
            yield from resp.awrite(html_header)
            yield from resp.awrite("Saved config.<br />")
            yield from resp.awrite('<form action="/restart" method="post"> \
                                   <button name="Restart">Connect to {}</button></form>'.format(ssid))

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
    obi_mqtt.do_connect()

# Show that we are ready
port_io.blink_led(40)
# Start web app
app.run(debug=True, port = 80,  host = '0.0.0.0')
