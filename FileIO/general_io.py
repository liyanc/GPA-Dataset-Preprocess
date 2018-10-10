"""
"""

__author__ = "Liyan Chen"


import pickle


def load_pkl(fname, python2=False):
    encoding="latin1" if python2 else "ASCII"

    with open(fname, "rb") as f:
        return pickle.load(f, encoding=encoding)


def dump_pkl(obj, fname):
    with open(fname, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)