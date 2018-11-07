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
        if int(key) in cfg.outputs.keys():
            print("INFO: switching port {} to {}".format(key, val))
            if val == 'on':
                port_io.set_output(int(key), 1)
            elif val == 'off':
                port_io.set_output(int(key), 0)
    status = port_io.get_ports_status()
    yield from picoweb.start_response(resp, content_type = "application/json")
    yield from resp.awrite(ujson.dumps(status))

@app.route('/toggle')
def toggle(req, resp):
    queryString = req.qs
    parameters = qs_parse(queryString)
    for key, val in parameters.items():
        if int(key) in cfg.outputs.keys():
            print("INFO: toggling port {} for {} seconds".format(key, val))
            port_io.toggle_output(int(key))
            time.sleep(float(val))
            port_io.toggle_output(int(key))
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
