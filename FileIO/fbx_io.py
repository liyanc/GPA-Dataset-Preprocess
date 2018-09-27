"""
"""

__author__ = "Liyan Chen"

import glob
import os


def list_fbx(rt_dir):
    name2path = {}
    for f in glob.iglob(rt_dir + "/*.fbx"):
        name2path[os.path.splitext(os.path.basename(f))[0]] = f

    return name2path
