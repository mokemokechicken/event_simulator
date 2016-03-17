# coding: utf8

import os
from pandas import json

import tensorflow as tf
import numpy as np

from event_simulator.lib.builder import build_model, train_model, DataFeeder, simulate_sequence
from event_simulator.lib.ptb_model import SmallConfig
from event_simulator.lib.util import ensure_base_dir


flags = tf.flags

# flags.DEFINE_string("dataset", None, "path to dataset")
flags.DEFINE_string("model", None, "path to model file")
# flags.DEFINE_boolean("padding", False, "use training data padding")
# flags.DEFINE_integer("num_steps", None, "num_steps")
flags.DEFINE_integer("num_sample", None, "number of samples to generate")
flags.DEFINE_string("output", None, "output path")
# flags.DEFINE_integer("hidden_size", None, "hidden_size")

FLAGS = flags.FLAGS


def main(unused_args):
    config = SmallConfig()
    model_path = FLAGS.model
    output_path = FLAGS.output
    np.random.seed()

    # data_loader
    if FLAGS.num_sample:
        config.batch_size = FLAGS.num_sample

    with tf.Graph().as_default(), tf.Session() as session:
        config.num_steps = 1
        model, model_validate = build_model(session, config, model_path)
        sequence_list = simulate_sequence(session, model_validate)
        if output_path:
            ensure_base_dir(output_path)
            with open(output_path, 'w') as f:
                json.dump(sequence_list, f)
        else:
            json.dumps(sequence_list)


if __name__ == '__main__':
    tf.app.run()