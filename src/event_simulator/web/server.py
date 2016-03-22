# coding: utf8
import sys
from pandas import json

from bottle import route, run, static_file, get, post, request

from event_simulator.lib.data_feeder import DataFeeder
from event_simulator.lib.ptb_model import SmallConfig
from event_simulator.web import config
from event_simulator.web.web_simulator import WebSimulator


PUBLIC_DIR = "%s/public" % config.WEB_DIR


def web_application(web_simulators, default_web_simulator):
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
        return {"events": default_web_simulator.get_event_list()}

    @post('/api/simulate')
    def simulate():
        json_body = request.json
        init_sequence = json_body['init_sequence']
        target_event_list = [json_body['target_event']]
        num_sample = int(json_body.get('num_sample', default_web_simulator.num_sample))

        web_simulator = web_simulators.get(num_sample)
        if not web_simulator:
            web_simulator = create_simulator(default_web_simulator.data_feeder,
                                            default_web_simulator.model_path,
                                            num_sample)
            web_simulators[num_sample] = web_simulator

        for event_name in target_event_list + init_sequence:
            if event_name not in web_simulator.data_feeder.mapping:
                return {"error": "Event %s is not found" % event_name}

        cnt_hash = web_simulator.simulate_sequence(init_sequence, target_event_list)
        return cnt_hash

    run(host='localhost', port=8080, debug=True, reloader=True)


def create_simulator(data_feeder, model_path, num_sample):
    simulator_config = SmallConfig()
    simulator_config.batch_size = num_sample

    with tf.Graph().as_default():
        web_simulator = WebSimulator()
        web_simulator.setup(data_feeder, tf.Session(), simulator_config, model_path)

    return web_simulator


######

import tensorflow as tf
import numpy as np

flags = tf.flags
flags.DEFINE_string("data", None, "path to data")
flags.DEFINE_string("model", None, "path to model file")
flags.DEFINE_integer("num_sample", 10000, "number of samples to generate")
FLAGS = flags.FLAGS


def main(unused_args):
    web_simulators = {}
    model_path = FLAGS.model
    data_path = FLAGS.data
    num_sample = FLAGS.num_sample
    if not model_path or not data_path:
        print('--model and --data are required')
        sys.exit(1)

    np.random.seed()

    # data_loader
    data_feeder = DataFeeder.load_from_base_path(data_path, config=None)  # only load mapping
    w = web_simulators[num_sample] = create_simulator(data_feeder, model_path, num_sample)
    web_application(web_simulators, w)


if __name__ == '__main__':
    tf.app.run()
