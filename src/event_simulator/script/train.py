# coding: utf8

import numpy as np
import pandas as pd
import tensorflow as tf

from event_simulator.lib.builder import build_model, train_model, DataFeeder, simulate_sequence
from event_simulator.lib.ptb_model import SmallConfig
from event_simulator.lib.util import ensure_base_dir

flags = tf.flags

flags.DEFINE_string("data", None, "path to data")
flags.DEFINE_string("model", None, "path to output model file")
flags.DEFINE_integer("num_steps", None, "num_steps")
flags.DEFINE_integer("batch_size", None, "batch_size")
flags.DEFINE_integer("epoch", 13, "epoch")
flags.DEFINE_integer("num_layers", None, "num_layers")
flags.DEFINE_integer("hidden_size", None, "hidden_size")

FLAGS = flags.FLAGS


def override_config(config):
    if FLAGS.batch_size: config.batch_size = FLAGS.batch_size
    if FLAGS.num_steps: config.num_steps = FLAGS.num_steps
    if FLAGS.num_layers: config.num_layers = FLAGS.num_layers
    if FLAGS.hidden_size: config.hidden_size = FLAGS.hidden_size
    if FLAGS.epoch: config.max_max_epoch = FLAGS.epoch
    return config


def main(unused_args):
    config = override_config(SmallConfig())
    if not FLAGS.data or not FLAGS.model:
        raise RuntimeError('--data and --model is required')
    data_path = FLAGS.data
    model_path = FLAGS.model
    separator = "\t" if ".tsv" in data_path else ','
    ensure_base_dir(model_path)

    with tf.Graph().as_default(), tf.Session() as session:
        data_feeder = DataFeeder.load_from_base_path(data_path, config)
        if not data_feeder:
            raw_data = pd.read_csv(data_path, sep=separator)
            data_feeder = DataFeeder(config)
            print("packaging data")
            data_feeder.pack_from_event_table(raw_data[['user_id', 'event']].values)
            data_feeder.save_to_base_path(data_path)

        config.vocab_size = data_feeder.vocabulary_size
        config.batch_size = data_feeder.batch_size
        print("VocabularySize=%s" % data_feeder.vocabulary_size)
        print("DataShape=%s" % repr(data_feeder.data.shape))
        print("padding rate=%s" % (1.0*np.sum(data_feeder.data == 0) / np.size(data_feeder.data)))
        model, model_validate = build_model(session, config, model_path)
        train_model(session, model, data_feeder)


if __name__ == '__main__':
    tf.app.run()