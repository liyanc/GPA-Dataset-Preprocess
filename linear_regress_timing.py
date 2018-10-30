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
parser.add_argument("timeparam_file", type=str)
parser.add_argument("camproj_dir", type=str)
args = parser.parse_args()
apath = fio.ArgPathBuilder(args)

subj, takename = args.subj_takename.split(",")
recalib_cam = input("Cameras to be recalibrated (separated by -): ").split("-")

cam_dict = fio.load_cam(apath.camparam_file)
imgdir_io = fio.ImgDirIO(apath.day_subdir, subj, takename)
viddir_io = fio.VideoDirIO(apath.day_subdir, subj, takename)
marker_io = fio.MarkerDirIO(apath.marker_dir)
joint_io = fio.BVHDirIO(apath.bvh_dir)
img_reader = fio.ImgProjReader(cam_dict, imgdir_io, viddir_io)
mkr_reader = fio.MarkerSkeletonProjReader(cam_dict, marker_io, joint_io, subj, takename)

timeparam_dict = {}
recalib_proj_dict = {}
time_corr_dict = fio.load_pkl(apath.timecorr_file)
for cam in ["00", "01", "02", "03", "04"]:
    scale, offset, total, inlier = camsolve.ransac_linear_regress(time_corr_dict[cam])
    print("{:}, inlier percentage: {:.2f}%, total: {:}".format(cam, inlier * 100.0 / total, total))
    if cam in recalib_cam:

        wind = ui.TimeAlignmentWindow(cam, img_reader, mkr_reader, 0, title_pretext="Correct Calibration")
        wind.load_affine_params((scale[0], offset))
        wind.run(auto_close=False)
        recalib_proj_dict[cam] = wind.get_pt_correspondence()

        # Recalibrate Cameras
        new_params = camsolve.calibrate_params(recalib_proj_dict[cam][0], recalib_proj_dict[cam][1])
        cam_dict[cam].load_params(new_params)
        img_reader = fio.ImgProjReader(cam_dict, imgdir_io, viddir_io)
        mkr_reader = fio.MarkerSkeletonProjReader(cam_dict, marker_io, joint_io, subj, takename)
        wind = ui.TimeAlignmentWindow(cam, img_reader, mkr_reader, 0, title_pretext="Verify Calibration")
        wind.load_affine_params((scale[0], offset))
        wind.run()

fio.dump_pkl(timeparam_dict, apath.timeparam_file)
fio.dump_pkl(fio.dump_cam(cam_dict), "{:}/{:}_{:}_camparams.pkl".format(apath.camproj_dir, subj, takename))
if recalib_cam:
    fio.dump_pkl(recalib_proj_dict, "{:}/{:}_{:}_camproj.pkl".format(apath.camproj_dir, subj, takename))