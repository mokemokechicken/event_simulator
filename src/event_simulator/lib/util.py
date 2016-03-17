# coding: utf8
import os

from scipy.stats import entropy
import numpy as np
from itertools import chain


def JSD(P, Q):
    _P = P / np.linalg.norm(P, ord=1)
    _Q = Q / np.linalg.norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))


def ensure_base_dir(path):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)


def flatten(nested_list):
    return list(chain.from_iterable(nested_list))
