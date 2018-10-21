"""
"""

__author__ = "Liyan Chen"

import glob
import os
from collections import defaultdict


class ImgDirIO:
    def __init__(self, rt_path, subj, take):
        ts_file = "{:}/{:}_{:}_timestamp.txt".format(rt_path, subj, take)
        img_dir = "{:}/{:}_{:}".format(rt_path, subj, take)
        img_list = glob.glob("{:}/*.bmp.lz4".format(img_dir))

        self.global_ts_to_cam_ts = defaultdict(dict)
        self.imgfile_timestamp = {"00": [], "01": [], "02": []}

        with open(ts_file, "r") as f:
            for line in f:
                cam, _, glob_ts, color_ts, depth_ts = line.strip().split()
                self.global_ts_to_cam_ts[int(glob_ts)][cam] = float(color_ts) * 1000.0

        for imgf in img_list:
            cam, glob_ts, imgid = os.path.basename(imgf).split(".")[0].split("-")
            self.imgfile_timestamp[cam].append((imgf, self.global_ts_to_cam_ts[int(glob_ts)][cam]))

        for cam in self.imgfile_timestamp:
            self.imgfile_timestamp[cam].sort(key=lambda x: x[1])

    def get_imgfile_timestamp(self, cam):
        return self.imgfile_timestamp[cam]

    def get_meta_from_name(self, filename):
        cam, glob_ts, imgid = os.path.basename(filename).split(".")[0].split("-")
        return cam, glob_ts, imgid