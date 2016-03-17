# coding: utf8

import os


import tensorflow as tf
import numpy as np

from event_simulator.lib.data_feeder import DataFeeder
from event_simulator.lib.ptb_model import SmallConfig
from event_simulator.lib.simulator import Simulator


flags = tf.flags

flags.DEFINE_string("data", None, "path to data")
flags.DEFINE_string("model", None, "path to model file")
flags.DEFINE_integer("num_sample", None, "number of samples to generate")
flags.DEFINE_boolean("show_events", False, "only show event list")
FLAGS = flags.FLAGS

TARGET_EVENT_LIST = ['_drop_out_', 'activities.shopping_complete', 'activities.entry_complete']


def main(unused_args):
    config = SmallConfig()
    model_path = FLAGS.model
    data_path = FLAGS.data
    if FLAGS.num_sample:
        config.batch_size = FLAGS.num_sample
    np.random.seed()

    # data_loader
    data_feeder = DataFeeder.load_from_base_path(data_path, config=None)  # only load mapping

    if FLAGS.show_events:
        show_events(data_feeder)
        return

    init_sequence = [x for x in unused_args if x in data_feeder.mapping]

    for event_name in TARGET_EVENT_LIST + init_sequence:
        if event_name not in data_feeder.mapping:
            print("Event %s is not found" % event_name)
            return

    with tf.Graph().as_default(), tf.Session() as session:
        simulator = Simulator(data_feeder, session, config, model_path)
        simulator.simulate_sequence(init_sequence, TARGET_EVENT_LIST)


def show_events(data_feeder):
    for event in data_feeder.mapping.keys():
        print(event)


if __name__ == '__main__':
    tf.app.run()
