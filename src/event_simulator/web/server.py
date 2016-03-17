# coding: utf8

from bottle import route, run, static_file
from event_simulator.web import config


PUBLIC_DIR = "%s/public" % config.WEB_DIR


@route('/')
def index():
    return static_file('index.html', root=PUBLIC_DIR)


@route('/<filename:re:.*\.html>')
def index(filename):
    return static_file(filename, root=PUBLIC_DIR)


@route('/public/<filename:path>')
def send_public(filename):
    return static_file(filename, root=PUBLIC_DIR)


run(host='localhost', port=8080, debug=True, reloader=True)
