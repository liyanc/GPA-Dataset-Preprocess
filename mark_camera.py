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
parser.add_argument("cam3_subdir", type=str)
parser.add_argument("cam4_subdir", type=str)
parser.add_argument("marker_file", type=str)
args = parser.parse_args()

# Initalize parameters
cam_proj = {}
# Kinect cameras
cam = "00"
imgdir = "{:}/{:}".format(args.root_dir, args.kinect_subdir)
mean_img = fio.lz4_mean_img(fio.list_img_cam(imgdir, cam))

with open("{:}/{:}".format(args.root_dir, args.marker_file), "rb") as f:
    unlabeled_dict = pickle.load(f, encoding="latin1")

cam_proj = ui.get_marker_id(mean_img, cam, unlabeled_dict, cam_proj)
print(cam_proj)