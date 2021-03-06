import machine
import network
import picoweb
import ujson
import utime
import uos
import gc
import uasyncio as asyncio
from . import config as cfg    # local module
from . import port_io          # local module
from . import obi_mqtt         # local module
from . import obi_html         # local module
from . import obi_time         # local module
from . import obi_tools        # local module

app = picoweb.WebApp(None)
conf = obi_tools.load_cfg()

@app.route('/status')
def get_status(req, resp):
    status = port_io.get_ports_status()
    yield from picoweb.start_response(resp, content_type = "application/json")
    yield from resp.awrite(ujson.dumps(status))

@app.route('/switch')
def switch(req, resp):
    req.parse_qs()
    for key, val in req.form.items():
        if key == 'pwr':
            if val[0] in ('on', 'off'):
                if val[0] == 'on':
                    port_io.set_output(cfg.RELAY, 1)
                elif val[0] == 'off':
                    port_io.set_output(cfg.RELAY, 0)
                port_io.set_output(cfg.LED_R, port_io.get_output(cfg.RELAY))
                obi_mqtt.publish_status(obi_mqtt.mqtt_client, conf, val[0])

    # redirect to "/"
    headers = {"Location": "/"}
    yield from picoweb.start_response(resp, status="303", headers=headers)

@app.route('/toggle')
def toggle(req, resp):
    gc.collect()
    req.parse_qs()
    for key, val in req.form.items():
        if key == 'duration':
            # toggle relay
            port_io.toggle_output(cfg.RELAY)
            # set LED accordingly
            port_io.set_output(cfg.LED_R, port_io.get_output(cfg.RELAY))
            obi_mqtt.publish_status(obi_mqtt.mqtt_client, conf, 'on' if port_io.get_output(cfg.RELAY) else 'off')
            # If we have a duration > 0 sleep and toggle again
            if float(val[0]) > 0:
                utime.sleep(float(val[0])) # FIXME: use uasyncio for non blocking delay
                #await asyncio.sleep(float(val[0]))
                port_io.toggle_output(cfg.RELAY)
                port_io.set_output(cfg.LED_R, port_io.get_output(cfg.RELAY))
                obi_mqtt.publish_status(obi_mqtt.mqtt_client, conf, 'on' if port_io.get_output(cfg.RELAY) else 'off')
    # redirect to "/"
    headers = {"Location": "/"}
    yield from picoweb.start_response(resp, status="303", headers=headers)

@app.route("/")
def index(req, resp):
    gc.collect()
    method = req.method
    if method == "POST":
        pass
    else:
        # GET
        yield from picoweb.start_response(resp)
        yield from resp.awrite(obi_html.html_header)
        yield from resp.awrite("<center><h1>Hi, this is {}</h1><hr />".format(conf[cfg.idx('hostname')]))
        yield from resp.awrite("Power is")
        if port_io.get_output(cfg.RELAY) == 1:
            yield from resp.awrite("<h2>ON</h2>")
        else:
            yield from resp.awrite("<h2>OFF</h2>")
        yield from resp.awrite(obi_html.html_action)
        yield from resp.awrite("</div></div></div></body></html>")
        gc.collect()


@app.route('/info')
def system(req, resp):
    method = req.method
    if method == "POST":
        pass
    else:
        # GET
        gc.collect()
        wlan = network.WLAN(network.STA_IF)
        status = port_io.get_ports_status()
        yield from picoweb.start_response(resp)
        yield from resp.awrite(obi_html.html_header)
        yield from resp.awrite("<h1>{} - System Info</h1>".format(conf[cfg.idx('hostname')]))
        yield from resp.awrite("<p><table style=\"max-height:800px\"><thead><th>Item</th><th>conf</th></thead>")
        yield from resp.awrite("<tr><td>Network config</td><td><code>{}</code></td></tr>".format(wlan.ifconfig()))
        yield from resp.awrite("<tr><td>Micropython version</td><td><code>{}</code></td></tr>".format(uos.uname()[3]))
        yield from resp.awrite("<tr><td>Bytes free</td><td><code>{}</code></td></tr>".format(gc.mem_free()))
        yield from resp.awrite("<tr><td>Initial MQTT connection status</td><td><code>{}</code></td></tr>".format(obi_mqtt.mqtt_con_status))
        yield from resp.awrite("<tr><td>Port status</td><td><code>{}</code></td></tr>".format(ujson.dumps(status)))
        now = obi_time.rtc.datetime()
        (year, month, day, weekday, hours, minutes, seconds, subseconds) = now
        yield from resp.awrite("<tr><td>Time</td><td><code>{}-{}-{} {:02}:{:02}:{:02}</code></td></tr>".format(year, month, day, hours, minutes, seconds))
        year, month, day, hours, minutes, seconds, weekday, yearday = obi_time.boot_time
        yield from resp.awrite("<tr><td>Boot time</td><td><code>{}-{}-{} {:02}:{:02}:{:02}</code></td></tr>".format(year, month, day, hours, minutes, seconds))
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
        yield from resp.awrite(obi_html.html_header)
        yield from resp.awrite("Restarting...<br />")
        await asyncio.sleep(3)
        machine.reset()

@app.route('/reset')
def reset_defaults(req, resp):
    global conf
    method=req.method
    if method == 'POST':
        yield from picoweb.start_response(resp)
        yield from resp.awrite(obi_html.html_header)
        yield from resp.awrite("Deleted config.<br />")
        yield from resp.awrite("<a href=\"/setup\">Setup</a> a wifi connection")
        yield from resp.awrite("</body></html>")
        obi_tools.clear_cfg()
        conf = obi_tools.load_cfg()

@app.route('/download_cfg')
def download_cfg(req, resp):
    yield from app.sendfile(resp, 'obi_socket.cfg', "application/octet-stream")

@app.route('/setup')
def setup(req, resp):
    gc.collect()
    method = req.method
    if method == "POST":
        yield from req.read_form_data()
        for k, v in req.form.items():
            # update conf values
            conf[cfg.idx(k)] = v[0]

        gc.collect()
        obi_tools.save_cfg(conf)
        yield from picoweb.start_response(resp)
        yield from resp.awrite(obi_html.html_header)
        yield from resp.awrite("Saved config.<br />")
        yield from resp.awrite('<form action="/restart" method="post" > \
                               <button name="Restart">Restart to apply changes</button></form>')

    else:
        # GET - show form
        yield from picoweb.start_response(resp)
        yield from resp.awrite(obi_html.html_header)
        yield from resp.awrite('</br><form id="wifi_config" method="post">')
        yield from resp.awrite('<fieldset><legend>Wifi Config</legend>')
        yield from resp.awrite('<div class="input-group vertical">')
        k = 0
        for v in conf[0:3]:
            if cfg.keys[k] == 'wifi_pw':
                yield from resp.awrite('{0}: <input name="{0}" type="password" value="{1}">'.format(cfg.keys[k], v))
            else:
                yield from resp.awrite('{0}: <input name="{0}" value="{1}">'.format(cfg.keys[k], v))
            k += 1
        yield from resp.awrite('<button type="submit" value="Save">Save</button>')
        yield from resp.awrite("</div></fieldset></form>")

        yield from resp.awrite('</br><form id="mqtt_config" method="post">')
        yield from resp.awrite('<fieldset><legend>System Config</legend>')
        yield from resp.awrite('<div class="input-group vertical">')
        k = 3
        for v in conf[3:6]:
            yield from resp.awrite('{0}: <input name="{0}" value="{1}">'.format(cfg.keys[k], v))
            k += 1
        yield from resp.awrite('<button type="submit" value="Save">Save</button>')
        yield from resp.awrite("</div></fieldset></form>")

        yield from resp.awrite('</br><form id="mqtt_config" method="post">')
        yield from resp.awrite('<fieldset><legend>MQTT Config</legend>')
        yield from resp.awrite('<div class="input-group vertical">')
        k = 6
        for v in conf[6:]:
            yield from resp.awrite('{0}: <input name="{0}" value="{1}">'.format(cfg.keys[k], v))
            k += 1
        yield from resp.awrite('<button type="submit" value="Save">Save</button>')
        yield from resp.awrite("</div></fieldset></form>")

        '''
        # hw_config drop down list
        yield from resp.awrite('{0}: <select name="{0}">'.format('hw_config'))
        for k in cfg.hw_configs:
            yield from resp.awrite('<option value="{0}">{0}</option>'.format(k))
        yield from resp.awrite('</select>')
        '''
        yield from resp.awrite("</div></form></body></html>")
    gc.collect()
