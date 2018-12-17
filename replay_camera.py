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
parser.add_argument("subj_takename", type=str)
parser.add_argument("day_subdir", type=str)
parser.add_argument("marker_dir", type=str)
parser.add_argument("bvh_dir", type=str)
parser.add_argument("camparam_file", type=str)
parser.add_argument("timecorr_file", type=str)
args = parser.parse_args()
apath = fio.ArgPathBuilder(args)

subj, takename = args.subj_takename.split(",")

cam_dict = fio.load_cam(apath.camparam_file)
imgdir_io = fio.ImgDirIO(apath.day_subdir, subj, takename)
viddir_io = fio.VideoDirIO(apath.day_subdir, subj, takename)
marker_io = fio.MarkerDirIO(apath.marker_dir)
joint_io = fio.BVHDirIO(apath.bvh_dir)
img_reader = fio.ImgProjReader(cam_dict, imgdir_io, viddir_io)
mkr_reader = fio.MarkerSkeletonProjReader(cam_dict, marker_io, joint_io, subj, takename)

time_corr_dict = fio.load_pkl(apath.timecorr_file)
for cam in ["00", "01", "02", "03", "04"]:
    scale, offset, total, inlier = camsolve.ransac_linear_regress(time_corr_dict[cam])
    print("{:}, inlier percentage: {:.2f}%, total: {:}".format(cam, inlier * 100.0 / total, total))

    wind = ui.TimeAlignmentWindow(cam, img_reader, mkr_reader, 0, title_pretext="Replay")
    wind.load_affine_params((scale[0], offset))
    wind.run()
