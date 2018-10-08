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

# Initalize parameters
cam_proj = {}

with open("{:}/{:}".format(args.root_dir, args.marker_file), "rb") as f:
    unlabeled_dict = pickle.load(f, encoding="latin1")

# Kinect cameras
for cam in ["00", "01", "02"]:
    imgdir = "{:}/{:}".format(args.root_dir, args.kinect_subdir)
    mean_img = fio.lz4_mean_img(fio.list_img_cam(imgdir, cam))
    cam_proj = ui.get_marker_id(mean_img, cam, unlabeled_dict, cam_proj)

for cam, filepath in [("03", args.cam3_filename), ("04", args.cam4_filename)]:
    mean_img = fio.video_mean_frame(filepath)
    cam_proj = ui.get_marker_id(mean_img, cam, unlabeled_dict, cam_proj)

print(cam_proj)