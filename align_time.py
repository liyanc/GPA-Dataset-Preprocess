"""
"""

__author__ = "Liyan Chen"

import argparse
import numpy as np
import FileIO as fio
import UI as ui
import Camera as camsolve
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import widgets as wdgt
from matplotlib import font_manager as fm

plt.style.use("ggplot")


parser = argparse.ArgumentParser()
parser.add_argument("root_dir", type=str)
parser.add_argument("day_subdir", type=str)
parser.add_argument("marker_dir", type=str)
parser.add_argument("camparam_file", type=str)
parser.add_argument("offset_file", type=str)
args = parser.parse_args()
apath = fio.ArgPathBuilder(args)

subj, takename = "liyan", "action_00"
replay = True

cam_dict = fio.load_cam(apath.camparam_file)
imgdir_io = fio.ImgDirIO(apath.day_subdir, subj, takename)
viddir_io = fio.VideoDirIO(apath.day_subdir, subj, takename)
marker_io = fio.MarkerDirIO(apath.marker_dir)
img_reader = fio.ImgProjReader(cam_dict, imgdir_io, viddir_io)
mkr_reader = fio.MarkerProjReader(cam_dict, marker_io, subj, takename)

if replay:
    offset_dict = fio.load_pkl(apath.offset_file)
    for cam in ["00", "01", "02", "03", "04"]:
        wind = ui.TimeAlignmentWindow(cam, img_reader, mkr_reader, offset_dict[cam])
        wind.run()
else:
    offset = 0
    offset_dict = {}
    for cam in ["00", "01", "02", "03", "04"]:
        if cam in ["03", "04"]:
            offset = 0
        wind = ui.TimeAlignmentWindow(cam, img_reader, mkr_reader, offset)
        offset = wind.run()
        offset_dict[cam] = offset
    fio.dump_pkl(offset_dict, apath.offset_file)
