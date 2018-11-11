from machine import Pin
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
      yield from picoweb.start_response(resp)
      yield from resp.awrite("Hi, this is {} <br />".format(os.uname()[0]))
      yield from resp.awrite("Version: {} <br />".format(os.uname()[3]))
      yield from resp.awrite("{} bytes free".format(gc.mem_free()))

port_io.blink_led()
app.run(debug=True, port = 80,  host = '0.0.0.0')
