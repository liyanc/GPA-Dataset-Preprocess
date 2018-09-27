"""
"""

__author__ = "Liyan Chen"

import argparse
import MayaLoader as ml
import FileIO as fio

parser = argparse.ArgumentParser()
parser.add_argument("in_path", type=str)
parser.add_argument("out_path", type=str)
args = parser.parse_args()

fname2path = fio.list_fbx(args.in_path)
for fname, path in fname2path.items():
    ml.load_file(path)
    unlabeled = ml.get_mean_pos_unlabeled(ml.load_unlabeled_temporal(ml.load_unlabeled()))
    ml.save_dict_file(unlabeled, args.out_path + "/{:}.pkl".format(fname))

ml.close_maya()