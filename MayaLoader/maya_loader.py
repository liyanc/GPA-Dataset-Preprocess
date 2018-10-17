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

marker_names = ["ARIEL", "RBHD", "LBHD", "RFHD", "LFHD", "C7", "LBSH", "LFSH", "LUPA", "LELB",
                "LIEL", "LWRE", "LOWR", "LIWR", "LOHAND", "LIHAND", "CLAV", "T10", "STRN",
                "RFSH", "RBSH", "RUPA", "RELB", "RIEL", "RWRE", "RIWR", "ROWR", "RIHAND",
                "ROHAND", "LFWT", "LBWT", "RFWT", "RBWT", "LMWT", "RMWT", "LHIP", "LKNE", "LKNI",
                "LSHN", "LHEL", "LANK", "LMT5", "LMT1", "LTOE", "RHIP", "RKNE", "RKNI", "RSHN",
                "RHEL", "RANK", "RMT5", "RMT1", "RTOE"]


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


def load_labeled_with_temporal():
    markers = pm.ls(regex="({:})".format("|".join(marker_names)))
    marker_dict = {}
    for mkr in markers:
        name = str(mkr.name())
        marker_dict[name] = {
            "loc": np.array(mkr.worldPosition.get()),
            "visible": mkr.visibility.get(),
            "temporalX": {},
            "temporalY": {},
            "temporalZ": {}
        }

    curves = pm.ls(regex="({:})_translate.*".format("|".join(marker_names)))
    for cur in curves:
        m = re.search("(\w+)_translate(.*)", cur.name())
        name, dim = str(m.group(1)), "temporal" + m.group(2)
        for f_ind in range(cur.numKeys()):
            t, v = np.int32(cur.getTime(f_ind)), np.float64(cur.getValue(f_ind))
            marker_dict[name][dim][t] = v

    for mkr_name in marker_dict.keys():
        mkr = marker_dict[mkr_name]
        max_frame = max(max(mkr["temporalX"].keys()), max(mkr["temporalY"].keys()), max(mkr["temporalZ"].keys()))
        vec_curve = np.zeros([max_frame + 1, 3], np.float64) + np.nan
        for ind in range(max_frame + 1):
            if all(ind in mkr[axis] for axis in ["temporalX", "temporalY", "temporalZ"]):
                for axis, dim in [("temporalX", 0), ("temporalY", 1), ("temporalZ", 2)]:
                    vec_curve[ind, dim] = mkr[axis][ind]
        marker_dict[mkr_name]["curve"] = vec_curve

    return marker_dict


def save_dict_file(dict_content, fname):
    with open(fname, "wb") as f:
        pickle.dump(dict_content, f, pickle.HIGHEST_PROTOCOL)


def close_maya():
    maya.standalone.uninitialize()