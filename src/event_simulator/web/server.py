# coding: utf8
import sys
from pandas import json

from bottle import route, run, static_file, get, post, request

from event_simulator.lib.data_feeder import DataFeeder
from event_simulator.lib.ptb_model import SmallConfig
from event_simulator.web import config
from event_simulator.web.web_simulator import WebSimulator


web_simulator = WebSimulator()

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


@get('/api/events')
def get_event_list():
    return {"events": web_simulator.get_event_list()}


@post('/api/simulate')
def simulate():
    json_body = request.json
    cnt_hash = web_simulator.simulate_sequence(json_body['init_sequence'], json_body['target_event'])
    return cnt_hash


######

import tensorflow as tf
import numpy as np

flags = tf.flags
flags.DEFINE_string("data", None, "path to data")
flags.DEFINE_string("model", None, "path to model file")
flags.DEFINE_integer("num_sample", 10000, "number of samples to generate")
FLAGS = flags.FLAGS


def main(unused_args):
    simulator_config = SmallConfig()
    model_path = FLAGS.model
    data_path = FLAGS.data
    if FLAGS.num_sample:
        simulator_config.batch_size = FLAGS.num_sample
    if not model_path or not data_path:
        print('--model and --data are required')
        sys.exit(1)

    np.random.seed()

    # data_loader
    data_feeder = DataFeeder.load_from_base_path(data_path, config=None)  # only load mapping

    with tf.Graph().as_default(), tf.Session() as session:
        web_simulator.setup(data_feeder, session, simulator_config, model_path)
        run(host='localhost', port=8080, debug=True, reloader=True)


if __name__ == '__main__':
    tf.app.run()
