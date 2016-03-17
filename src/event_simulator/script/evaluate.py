#!/usr/bin/env python
# coding: utf-8
"""Compare data distribution"""

import json
from collections import defaultdict

import tensorflow as tf
import pandas as pd

from event_simulator.lib.data_feeder import DataFeeder
from event_simulator.lib.evaluator import compare_data

flags = tf.flags
logging = tf.logging

flags.DEFINE_string("data", None, "path to data")
flags.DEFINE_string("sample", None, "path to sampling data")
flags.DEFINE_string("figure", 'fig.png', 'path to output figure image')

FLAGS = flags.FLAGS


def load_and_convert_to_event_sequence(dataset_path):
    if '.csv' in dataset_path:
        return load_event_table(dataset_path, ',')
    if '.tsv' in dataset_path:
        return load_event_table(dataset_path, "\t")
    else:
        raise NotImplementedError()


def load_event_table(data_path, separator):
    df = pd.read_csv(data_path, sep=separator)
    seq_hash = defaultdict(lambda: [])
    for row in df.values:
        seq_hash[row[0]].append(row[1])
    return seq_hash.values()


def main(unused_args):
    data_path = FLAGS.data
    sampling_data_path = FLAGS.sample
    fig_path = FLAGS.figure
    if not data_path or not sampling_data_path:
        raise ValueError("Must set --data and --sample")

    true_data = load_and_convert_to_event_sequence(data_path)
    data_feeder = DataFeeder.load_from_base_path(data_path, config=None)  # only load mapping
    with open(sampling_data_path, 'r') as f:
        sampling_data = json.load(f)
    id_to_name_mapping = data_feeder.id_to_name_mapping()
    sampling_data_by_event_name = []
    for sequence in sampling_data:
        sampling_data_by_event_name.append([id_to_name_mapping[k] for k in sequence])

    compare_data(fig_path, true_data, sampling_data_by_event_name, graph_scape=4)


if __name__ == '__main__':
    tf.app.run()