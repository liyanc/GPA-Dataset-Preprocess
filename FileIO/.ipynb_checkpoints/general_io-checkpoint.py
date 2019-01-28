"""
"""

__author__ = "Liyan Chen"


import pickle
import Camera as camsolve


def load_pkl(fname, python2=False):
    encoding="latin1" if python2 else "ASCII"

    with open(fname, "rb") as f:
        return pickle.load(f, encoding=encoding)


def dump_pkl(obj, fname):
    with open(fname, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_cam(camparam_file):
    cam_dict = {}
    param_dict = load_pkl(camparam_file)
    for cam, param in param_dict.items():
        csolver = camsolve.CameraSolverNonlinear()
        csolver.load_params(param)
        cam_dict[cam] = csolver
    return cam_dict


def dump_cam(cam_dict):
    return dict((k, v.dump_params) for k, v in cam_dict.items())


class ArgPathBuilder:
    def __init__(self, args):
        self.args = args

    def __getattr__(self, item):
        return "{:}/{:}".format(self.args.root_dir, vars(self.args)[item])

