"""
"""

__author__ = "Liyan Chen"

import matplotlib
import argparse
import pickle
import FileIO as fio
import UI as ui
from matplotlib import pyplot as plt
import matplotlib.patches as ptch

plt.style.use("ggplot")

parser = argparse.ArgumentParser()
parser.add_argument("root_dir", type=str)
parser.add_argument("kinect_subdir", type=str)
parser.add_argument("cam3_filename", type=str)
parser.add_argument("cam4_filename", type=str)
parser.add_argument("marker_file", type=str)
parser.add_argument("camproj_outfile", type=str)
args = parser.parse_args()
apath = fio.ArgPathBuilder(args)

# Initalize parameters
cam_proj = {}

unlabeled_dict = fio.load_pkl(apath.marker_file, True)

target_cam = input("Input cameras to be marked (separated by\'-\'): ").strip().split("-")

# Kinect cameras
for cam in ["00", "01", "02"]:
    imgdir = apath.kinect_subdir
    if cam in target_cam:
        mean_img = fio.lz4_mean_img(fio.list_img_cam(imgdir, cam))
        cam_proj = ui.get_marker_id(mean_img, cam, unlabeled_dict, cam_proj)

for cam, filepath in [
    ("03", apath.cam3_filename),
    ("04", apath.cam4_filename)]:
    if cam in target_cam:
        mean_img = fio.video_mean_frame(filepath)
        cam_proj = ui.get_marker_id(mean_img, cam, unlabeled_dict, cam_proj)

fio.dump_pkl(cam_proj, "{:}/{:}".format(args.root_dir, args.camproj_outfile))