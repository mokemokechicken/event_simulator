#!/usr/bin/env python
# coding: utf-8
import math
import os
import pickle
from collections import defaultdict
from operator import itemgetter

import numpy as np
from numpy import random

from event_simulator.lib.util import flatten

__author__ = 'k_morishita'


class DataFeeder:
    PAD_ID = 0
    START_ID = 1
    END_ID = 2

    def __init__(self, config=None):
        if config:
            self._num_steps = config.num_steps + 1
            self._batch_size = config.batch_size
            self._mapping = {
                "_pad_": self.PAD_ID,
                "_start_": self.START_ID,
                "_end_": self.END_ID,
            }
        self._data = None

    # @property
    # def config(self):
    #     self._config.mapping = self.mapping
    #     self._config.vocab_size = self.vocabulary_size
    #     return self._config
    #
    @property
    def vocabulary_size(self):
        return len(self.mapping)

    @property
    def num_steps(self):
        return self._num_steps

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def mapping(self):
        return self._mapping

    @property
    def epoch_size(self):
        return self.data.shape[1] / self.num_steps

    def id_to_name_mapping(self):
        ret = {}
        for k, v in self.mapping.items():
            ret[v] = k
        return ret

    @property
    def data(self):
        """

        :rtype: numpy.array
        """
        return self._data

    def __iter__(self):
        self.step_index = -1
        return self

    def __next__(self):
        self.step_index += 1
        num_steps = self.num_steps
        i = self.step_index
        if self.epoch_size <= i:
            raise StopIteration
        x = self.data[:, i * num_steps    :(i + 1) * num_steps - 1]
        y = self.data[:, i * num_steps + 1:(i + 1) * num_steps]
        return x, y

    def batch_list_of_starting_flag(self):
        return self.data[:, self.step_index * self.num_steps] == self.START_ID

    def next_event_id(self):
        return len(self.mapping)

    def pack_from_event_table(self, event_table):
        """

        :param event_table: numpy array of [user_id, event_name]
        """

        seq_hash = defaultdict(lambda: [])
        for seq_id, event_name in event_table:
            seq_hash[seq_id].append(self.event_name_to_id(event_name))
        self.pack_from_seq_hash(seq_hash)

    def pack_from_seq_hash(self, seq_hash):
        num_steps = self.num_steps
        batch_size = self.batch_size
        seq_len_hash = {}
        for seq_id, sequence in seq_hash.items():
            seq_hash[seq_id] = s = self.padding_sequence([self.START_ID] + sequence + [self.END_ID], num_steps)
            seq_len_hash[seq_id] = len(s)

        total_len = sum(seq_len_hash.values())
        max_len = total_len // batch_size
        batch_lines = [[] for _ in range(batch_size)]
        batch_lines_length = [0] * batch_size

        # not good algorithm...
        for seq_id, seq_len in sorted(seq_len_hash.items(), key=itemgetter(1), reverse=True):
            sequence = seq_hash[seq_id]
            while not self.append_sequence(batch_lines, batch_lines_length, sequence, max_len):
                max_len += 1

        real_batch_lines = []
        for line in batch_lines:
            if len(line) > 0:
                random.shuffle(line)
                real_batch_lines.append(flatten(line))
        self.padding_to_max_len(real_batch_lines, max_len)
        self._data = self.convert_to_np_array(real_batch_lines)
        if self.batch_size != len(real_batch_lines):
            print("change batch_size from %s to %s" % (self.batch_size, len(real_batch_lines)))
            self._batch_size = len(real_batch_lines)

    @staticmethod
    def append_sequence(batch_lines, batch_lines_length, sequence, max_len):
        for i, line in enumerate(batch_lines):
            if batch_lines_length[i] + len(sequence) <= max_len:
                line.append(sequence)
                batch_lines_length[i] += len(sequence)
                # if random.random() < 0.5:
                #     line.extend(sequence)
                # else:
                #     line[:0] = sequence
                return True
        return False

    def padding_to_max_len(self, batch_lines, max_len):
        # PADDING to max_len
        for line in batch_lines:
            if len(line) < max_len:
                line.extend([self.PAD_ID] * (max_len-len(line)))

    def convert_to_np_array(self, batch_lines):
        data_type = np.uint
        if len(self.mapping) < 256:
            data_type = np.uint8
        elif len(self.mapping) < 65536:
            data_type = np.uint16
        return np.array(batch_lines, data_type)

    def padding_sequence(self, sequence, num_steps):
        padded_len = int(math.ceil(len(sequence) / num_steps) * num_steps)
        return sequence + ([self.PAD_ID] * (padded_len - len(sequence)))

    def event_name_to_id(self, event_name):
        event_id = self.mapping.get(event_name, None)
        if event_id is not None:
            return event_id
        event_id = self.mapping[event_name] = self.next_event_id()
        return event_id

    @classmethod
    def load_from_base_path(cls, path, config=None):
        data_feeder = cls()
        if not data_feeder._load_mapping_from_base_path(path):
            return None

        if config:
            p = "%s.ns_%s-bs_%s" % (path, config.num_steps + 1, config.batch_size)
            if data_feeder._load_data_config_from_base_path(p) and data_feeder._load_data_from_base_path(p):
                return data_feeder
            else:
                return None
        else:
            return data_feeder

    def save_to_base_path(self, path):
        self._save_mapping_to_base_path(path)
        p = "%s.ns_%s-bs_%s" % (path, self.num_steps, self.batch_size)
        self._save_data_config_to_base_path(p)
        self._save_data_to_base_path(p)

    def _save_data_config_to_base_path(self, path):
        with open("%s.config" % path, "wb") as f:
            self.save_config(f)

    def _load_data_config_from_base_path(self, path):
        print("loading config")
        p = "%s.config" % path
        if os.path.exists(p):
            with open("%s.config" % path, "rb") as f:
                self.load_config(f)
            return True

    def _save_mapping_to_base_path(self, path):
        with open("%s.mapping" % path, "wb") as f:
            self.save_mapping(f)

    def _load_mapping_from_base_path(self, path):
        print("loading mapping")
        p = "%s.mapping" % path
        if os.path.exists(p):
            with open(p, "rb") as f:
                self.load_mapping(f)
            return True

    def _save_data_to_base_path(self, path):
        with open("%s.packed" % path, "wb") as f:
            self.save_data(f)

    def _load_data_from_base_path(self, path):
        print("loading packed data")
        p = "%s.packed" % path
        if os.path.exists(p):
            with open(p, "rb") as f:
                self.load_data(f)
            return True

    def save_config(self, f):
        pickle.dump({
            "num_steps": self.num_steps,
            "batch_size": self.batch_size,
        }, f)

    def load_config(self, f):
        config = pickle.load(f)
        self._num_steps = config['num_steps']
        self._batch_size = config['batch_size']

    def save_mapping(self, f):
        pickle.dump(self.mapping, f)

    def load_mapping(self, f):
        self._mapping = pickle.load(f)

    def save_data(self, f):
        pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_data(self, f):
        self._data = pickle.load(f)