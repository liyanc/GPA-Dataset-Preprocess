"""
"""

__author__ = "Liyan Chen"

import argparse
import cv2
import numpy as np
import FileIO as fio
import UI as ui
import Camera as camsolve
from matplotlib import pyplot as plt

plt.style.use("ggplot")

parser = argparse.ArgumentParser()
parser.add_argument("root_dir", type=str)
parser.add_argument("kinect_subdir", type=str)
parser.add_argument("cam3_filename", type=str)
parser.add_argument("cam4_filename", type=str)
parser.add_argument("marker_file", type=str)
parser.add_argument("camproj_file", type=str)
parser.add_argument("camparam_file", type=str)
parser.add_argument("report_file", type=str)
parser.add_argument("side_out_prefix", type=str)
args = parser.parse_args()
apath = fio.ArgPathBuilder(args)

unlabeled_dict = fio.load_pkl("{:}/{:}".format(args.root_dir, args.marker_file), True)
cam_proj = fio.load_pkl("{:}/{:}".format(args.root_dir, args.camproj_file))
solv_params = {}

fig = plt.figure(figsize=(20, 28))
fig.suptitle("Calibration Quality of {:}".format(args.kinect_subdir))
figind = 0
for cam, filepath in [
    ("03", "{:}/{:}".format(args.root_dir, args.cam3_filename)),
    ("04", "{:}/{:}".format(args.root_dir, args.cam4_filename))]:

    # Load Image and its parameters
    mean_img = fio.video_mean_frame(filepath)
    img_size = np.array(mean_img.shape[:2])
    init_c = img_size / 2

    # Build correspondences and solve
    p_world, q_proj = camsolve.build_pt_correspondence(cam_proj, unlabeled_dict, cam)
    csolver = camsolve.CameraSolverNonlinear(init_f=(1032, 1032), init_c=tuple(init_c), img_size=tuple(img_size))
    csolver.solve(p_world.T, q_proj.T)
    solv_params[cam] = csolver.dump_params()

    # Visualize the result
    figind += 1
    linear_img = csolver.undistort_img(mean_img)
    linear_pts = csolver.undistort_pts(q_proj.T)
    reproj = csolver.project_linear(p_world.T)
    cv2.imwrite(apath.side_out_prefix + "_{:}.png".format(cam), linear_img * 255.0)

    ax = fig.add_subplot(5, 2, figind)
    ui.show_clicks_reporj_on_img(ax, linear_img, linear_pts, reproj, cam)

    figind += 1
    ax = fig.add_subplot(5, 2, figind)
    ui.show_hist_reproj_err(ax, csolver, p_world, q_proj)


# Kinect cameras
for cam in ["00", "01", "02"]:
    imgdir = "{:}/{:}".format(args.root_dir, args.kinect_subdir)
    mean_img = fio.lz4_mean_img(fio.list_img_cam(imgdir, cam))
    img_size = np.array(mean_img.shape[:2])
    init_c = img_size / 2


    # Build correspondences and solve
    p_world, q_proj = camsolve.build_pt_correspondence(cam_proj, unlabeled_dict, cam)
    csolver = camsolve.CameraSolverNonlinear(init_f=(1032, 1032), init_c=tuple(init_c), img_size=tuple(img_size))
    csolver.solve(p_world.T, q_proj.T)
    solv_params[cam] = csolver.dump_params()

    # Visualize the result
    figind += 1
    linear_img = csolver.undistort_img(mean_img)
    linear_pts = csolver.undistort_pts(q_proj.T)
    reproj = csolver.project_linear(p_world.T)
    cv2.imwrite(apath.side_out_prefix + "_{:}.png".format(cam), linear_img * 255.0)

    ax = fig.add_subplot(5, 2, figind)
    ui.show_clicks_reporj_on_img(ax, linear_img, linear_pts, reproj, cam)

    figind += 1
    ax = fig.add_subplot(5, 2, figind)
    ui.show_hist_reproj_err(ax, csolver, p_world, q_proj)

fio.dump_pkl(solv_params, "{:}/{:}".format(args.root_dir, args.camparam_file))
plt.savefig("{:}/{:}".format(args.root_dir, args.report_file))
