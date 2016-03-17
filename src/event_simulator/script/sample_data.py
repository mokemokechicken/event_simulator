# coding: utf8

import random

import sys
import tensorflow as tf

flags = tf.flags
flags.DEFINE_integer("num_sample", 10000, "number of samples")
flags.DEFINE_integer("num_kind", 10, "number of kinds")
flags.DEFINE_integer("max_len", 1000, "max length of a sequence")
flags.DEFINE_float("terminate_rate", 0.05, "termination rate of a sequence")
flags.DEFINE_string("output", None, "output path")
FLAGS = flags.FLAGS


def generate_seq(event_kind_size, max_length, terminate_rate=0.05):
    ret = [0]
    for _ in range(max_length):
        rand = random.random()
        if rand < terminate_rate:
            break
        elif rand < 0.6:
            ret.append((ret[-1] + 1) % event_kind_size)
        else:
            n = (ret[-1] % 5) + 1  # 1~5
            ref = ret[-min(n, len(ret))]  # 直近のn番目の数字
            ret.append((ref + 1) % event_kind_size)
    return ["e%s" % x for x in ret]


def main():
    num_sample = FLAGS.num_sample
    num_kind = FLAGS.num_kind
    max_len = FLAGS.max_len
    terminate_rate = FLAGS.terminate_rate
    output_path = FLAGS.output

    f = sys.stdout
    if output_path:
        f = open(output_path, 'w')

    print("user_id,event", file=f)
    for n in range(num_sample):
        for ev in generate_seq(num_kind, max_len, terminate_rate):
            print("u%s,%s" % (n, ev), file=f)


if __name__ == '__main__':
    main()
