# coding: utf8
import os
import pickle
import gzip
from collections import Counter

from event_simulator.lib.util import ensure_base_dir
from .builder import build_model, simulate_sequence
import hashlib


class Simulator:
    def __init__(self, data_feeder, session, config, model_path):
        self.data_feeder = data_feeder
        self.session = session
        self.config = config
        self.model_path = model_path
        self.config.num_steps = 1
        self.num_sample = config.batch_size
        _, self.model = build_model(self.session, self.config, self.model_path)

    def simulate_sequence(self, init_sequence, target_event_list):
        sequence_list = self.simulate(init_sequence)
        cnt_hash = self.get_count_hash(sequence_list, target_event_list)
        count_hash = cnt_hash['count_hash']
        target_next_hash = cnt_hash['target_next_hash']
        not_target_next_hash = cnt_hash['not_target_next_hash']
        next_hash = self.get_next_event_hash(sequence_list)

        print("============= Target Event =================")
        for event_name in target_event_list:
            cnt = count_hash[event_name]
            print("%s -- count=%s percentage=%.2f%%" % (event_name, cnt, cnt / self.num_sample * 100))

            print(" == target ==")
            for next_event_name, n_cnt in sorted(target_next_hash[event_name].items(), key=lambda x: -x[1])[:5]:
                if n_cnt / cnt < 0.01:
                    break
                print("       %s -- count=%s percentage=%.2f%%" % (next_event_name, n_cnt, n_cnt / cnt * 100))

            print(" == NOT target ==")
            for next_event_name, n_cnt in sorted(not_target_next_hash[event_name].items(), key=lambda x: -x[1])[:5]:
                if n_cnt / cnt < 0.01:
                    break
                print("       %s -- count=%s percentage=%.2f%%" % (next_event_name, n_cnt, n_cnt / (self.num_sample - cnt) * 100))

        print("============= Next Event =================")
        for event_name, cnt in sorted(next_hash.items(), key=lambda x: -x[1]):
            if cnt / self.num_sample < 0.001:
                break
            print("%s -- count=%s percentage=%.2f%%" % (event_name, cnt, cnt / self.num_sample * 100))

    @property
    def cache_dir(self):
        return "%s.simulate%d_cache" % (self.model_path, self.num_sample)

    def cache_path(self, init_sequence):
        return "%s/%s.gz" % (self.cache_dir, self.digest("\t".join(init_sequence)))

    @staticmethod
    def digest(s):
        return hashlib.sha256(str(s).encode('utf8')).hexdigest()

    def simulate(self, init_sequence):
        cache_path = self.cache_path(init_sequence)
        ensure_base_dir(cache_path)
        if os.path.exists(cache_path):
            with gzip.open(cache_path, "rb") as f:
                return pickle.load(f)
        sequence_list = simulate_sequence(self.session, self.model,
                                          list(map(self.data_feeder.event_name_to_id, init_sequence)))
        with gzip.open(cache_path, "wb") as f:
            pickle.dump(sequence_list, f, protocol=pickle.HIGHEST_PROTOCOL)
        return sequence_list

    def get_count_hash(self, sequence_list, target_event_list):
        count_hash = {}
        target_next_hash = {}
        not_target_next_hash = {}
        rev = self.data_feeder.id_to_name_mapping()
        for event_name in target_event_list:
            target_counter = target_next_hash[event_name] = Counter()
            not_target_counter = not_target_next_hash[event_name] = Counter()
            count_id = self.data_feeder.event_name_to_id(event_name)
            cnt = 0
            for seq in sequence_list:
                if count_id in seq:
                    cnt += 1
                    self.increment_first_seq(target_counter, seq, rev)
                else:
                    self.increment_first_seq(not_target_counter, seq, rev)
            count_hash[event_name] = cnt
        return {"count_hash": count_hash, "target_next_hash": target_next_hash, "not_target_next_hash": not_target_next_hash}

    def get_next_event_hash(self, sequence_list):
        counter = Counter()
        rev = self.data_feeder.id_to_name_mapping()
        for seq in sequence_list:
            self.increment_first_seq(counter, seq, rev)
        return counter

    @staticmethod
    def increment_first_seq(counter, seq, rev, num=1):
        if len(seq) > 0:
            counter[rev[seq[0]]] += num
        else:
            counter['END'] += num

