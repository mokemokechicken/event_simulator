#!/usr/bin/env python
# coding: utf-8
"""Compare data distribution"""

from itertools import chain

import matplotlib.pyplot as plt
import pandas as pd

from event_simulator.lib.util import JSD


def check_length(ax, true_data, sampling_data):
    d1 = pd.DataFrame([len(x) for x in true_data])
    d2 = pd.DataFrame([len(x) for x in sampling_data])
    d1.columns = ['len']
    d2.columns = ['len']
    # cal JSD
    z1 = pd.value_counts(d1.len)
    z2 = pd.value_counts(d2.len)
    len_min = min(z1.index.min(), z2.index.min())
    len_max = max(z1.index.max(), z2.index.max())

    z = pd.concat({"d1": z1, "d2": z2}, axis=1, join_axes=[range(len_min, len_max)])
    z.fillna(0, inplace=True)
    jsd = JSD(z.d1, z.d2)

    d1.len.plot(ax=ax, kind="kde", label="true_data")
    d2.len.plot(ax=ax, kind="kde", label="sampling_data")
    ax.legend()
    ax.set_xlim((1, 50))
    ax.set_title("Length(JSD: %.5f)" % jsd)


def check_frequency(ax, true_data, sampling_data):
    true_seq = list(chain.from_iterable(true_data))
    sampling_seq = list(chain.from_iterable(sampling_data))

    f1 = pd.value_counts(true_seq) / len(true_seq)
    f2 = pd.value_counts(sampling_seq) / len(sampling_seq)
    freq = merge_and_sort(f1, f2)

    jsd = JSD(freq.true_data, freq.sampling_data)
    freq.index = [str(x)[:20] for x in freq.index]
    freq.plot(ax=ax, kind='bar')
    ax.set_title("Frequency(JSD: %.5f)" % jsd)


def check_pair(ax, true_data, sampling_data):
    # true_seq = list(chain.from_iterable(true_data))
    # sampling_seq = list(chain.from_iterable(sampling_data))
    #
    # true_pairs     = list(map(lambda x: "-".join([str(z) for z in x]), zip(true_seq[:-1], true_seq[1:])))
    # sampling_pairs = list(map(lambda x: "-".join([str(z) for z in x]), zip(sampling_seq[:-1], sampling_seq[1:])))

    true_pairs = create_2_gram(true_data)
    sampling_pairs = create_2_gram(sampling_data)

    p1 = pd.value_counts(true_pairs) / len(true_pairs)
    p2 = pd.value_counts(sampling_pairs) / len(sampling_pairs)
    freq = merge_and_sort(p1, p2)

    jsd = JSD(freq.true_data, freq.sampling_data)
    freq.index = [str(x)[:20] for x in freq.index]
    freq.plot(ax=ax, kind='bar')
    ax.set_xlim((-1, 40))
    ax.set_title("Pair(JSD: %.5f)" % jsd)


def merge_and_sort(s1, s2):
    freq = pd.concat([s1, s2], axis=1)
    freq.columns = ["true_data", "sampling_data"]
    freq.fillna(0, inplace=True)
    freq['sum'] = freq.true_data + freq.sampling_data
    freq.sort_values(['sum'], ascending=[False], inplace=True)
    del freq['sum']
    return freq


def create_2_gram(sequence_list):
    ret = []
    for sequence in sequence_list:
        ret.extend(list(map(lambda x: "-".join([str(z) for z in x]), zip(sequence[:-1], sequence[1:]))))
    return ret


def compare_data(fig_path, true_data, sampling_data, graph_scape=1):
    fig = plt.figure(figsize=(12*graph_scape, 9*graph_scape))
    ax1 = fig.add_subplot(3, 1, 1)
    ax2 = fig.add_subplot(3, 1, 2)
    ax3 = fig.add_subplot(3, 1, 3)
    check_length(ax1, true_data, sampling_data)
    check_frequency(ax2, true_data, sampling_data)
    check_pair(ax3, true_data, sampling_data)
    fig.tight_layout()
    # fig.show()
    fig.savefig(fig_path)

