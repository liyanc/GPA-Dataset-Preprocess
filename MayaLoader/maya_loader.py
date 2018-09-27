"""
"""

__author__ = "Liyan Chen"


import re
import pickle
import numpy as np
import maya.standalone
maya.standalone.initialize(name="python")
import pymel
import pymel.core as pm
import maya.mel as mmel
import maya.cmds as cmds

pm.loadPlugin("fbxmaya")


def load_file(fname):
    pm.newFile(f=1)
    pm.mel.FBXImport(f=fname)


def load_unlabeled():
    unlbl_markers = pm.ls(regex="_\d+Shape")
    unlabeled_dict = {}
    for mkr in unlbl_markers:
        idx = int(re.search("_(\d+)Shape", mkr.name()).group(1))
        unlabeled_dict[idx] = {
            "loc": np.array(mkr.worldPosition.get()),
            "visible": mkr.visibility.get(),
            "temporalX": {},
            "temporalY": {},
            "temporalZ": {}
        }

    return unlabeled_dict


def load_unlabeled_temporal(unlabeled_dict):
    mkr_curves = pm.ls(regex="_\d+_translate.*")
    for cur in mkr_curves:
        m = re.search("_(\d+)_translate(.*)", cur.name())
        idx, dim = int(m.group(1)), "temporal" + m.group(2)
        for f_ind in range(cur.numKeys()):
            t, v = np.float64(cur.getTime(f_ind)), np.float64(cur.getValue(f_ind))
            unlabeled_dict[idx][dim][t] = v

    return unlabeled_dict


def get_mean_pos_unlabeled(unlabeled_dict):
    for idx, record in unlabeled_dict.items():
        xs = record["temporalX"].values() + [record["loc"][0]]
        ys = record["temporalY"].values() + [record["loc"][1]]
        zs = record["temporalZ"].values() + [record["loc"][2]]
        mean_loc = np.array([np.mean(xs), np.mean(ys), np.mean(zs)])
        unlabeled_dict[idx]["mean"] = mean_loc

    return unlabeled_dict


def save_dict_file(dict_content, fname):
    with open(fname, "wb") as f:
        pickle.dump(dict_content, f, pickle.HIGHEST_PROTOCOL)


def close_maya():
    maya.standalone.uninitialize()