"""
"""

__author__ = "Liyan Chen"

import glob
import os
import re
import FileIO as fio
import numpy as np
from collections import defaultdict
from .marker_name import *


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


class MarkerDirIO:

    def __init__(self, rt_path):
        self.subj_take_file = defaultdict(dict)
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")
        for f in glob.glob("{:}/*.pkl".format(rt_path)):
            fname = os.path.basename(f)
            sub = fname.split("_")[0]
            take = ptn.search(fname).group(0)
            self.subj_take_file[sub][take] = f

    def list_subjects(self):
        return list(self.subj_take_file.keys())

    def list_takes_of_subject(self, subj):
        return list(self.subj_take_file[subj].keys())

    def load_marker_dict(self, subj, take):
        return fio.load_pkl(self.subj_take_file[subj][take], True)

    def load_marker_curve(self, subj, take):
        marker_dict = self.load_marker_dict(subj, take)
        curv_list = [marker_dict[mname]["curve"] for mname in id2marker]
        max_len = max(c.shape[0] for c in curv_list)
        curv_list = [np.pad(c, ((0, max_len - c.shape[0]), (0, 0)), "constant", constant_values=np.nan) for c in
                     curv_list]
        skel_curv = np.array(curv_list).transpose((1, 0, 2))
        return skel_curv


class BVHDirIO:
    def __init__(self, rt_path):
        self.subj_take_file = defaultdict(dict)
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")
        for f in glob.glob("{:}/*.mat".format(rt_path)):
            fname = os.path.basename(f)
            sub = fname.split("_")[0]
            take = ptn.search(fname).group(0)
            self.subj_take_file[sub][take] = f




class VideoDirIO:
    def __init__(self, rt_path, assigned_subj, assigned_take):
        self.cam_subj_take_file = {"03": defaultdict(dict), "04": defaultdict(dict)}
        self.cam_reader = {}
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")
        for cam_name, cam in [("camera3", "03"), ("camera4", "04")]:
            for f in glob.glob("{:}/{:}/*.MP4".format(rt_path, cam_name)):
                fname = os.path.basename(f)
                sub = fname.split("_")[0]
                match = ptn.search(fname)
                if match is not None:
                    take = match.group(0)
                    self.cam_subj_take_file[cam][sub][take] = f
            self.cam_reader[cam] = fio.VideoReader(self.cam_subj_take_file[cam][assigned_subj][assigned_take])


    def list_subjects(self, cam):
        return list(self.cam_subj_take_file[cam].keys())

    def list_takes_of_subject(self, cam, subj):
        return list(self.cam_subj_take_file[cam][subj].keys())

    def read_cam_frame_ts(self, cam, ind):
        return self.cam_reader[cam].read_frame_ts(ind)

    def get_max_frame(self, cam):
        return self.cam_reader[cam].get_max_frame()

    def close(self, cam):
        self.cam_reader[cam].close()


class ImgProjReader:
    equiv_mocap_frame = {"00": 4, "01": 4, "02": 4, "03": 4, "04":4}
    kinect_cam = ["00", "01", "02"]

    def __init__(self, cam_dict, imgdir_io, viddir_io):
        self.cam_dict = cam_dict
        self.imgdir_io = imgdir_io
        self.viddir_io = viddir_io

    def read_img_ts(self, ind, cam):
        # In case where camera is a kinect one
        if cam in self.kinect_cam:
            imgfile, imgts = self.imgdir_io.get_imgfile_timestamp(cam)[ind]
            return self.cam_dict[cam].undistort_img(fio.imread_from_lz4(imgfile)), imgts
        else:
            frame, ts = self.viddir_io.read_cam_frame_ts(cam, ind)
            return self.cam_dict[cam].undistort_img(frame), ts

    def get_frame_num_for_cam(self, cam):
        if cam in self.kinect_cam:
            return len(self.imgdir_io.get_imgfile_timestamp(cam))
        else:
            return self.viddir_io.get_max_frame(cam)

    def get_equiv_mocap_frame(self, cam):
        return self.equiv_mocap_frame[cam]

    def close(self, cam):
        self.viddir_io.close(cam)


class MarkerProjReader:
    def __init__(self, cam_dict, marker_io, subj, takename):
        self.cam_dict = cam_dict
        self.marker_io = marker_io
        self.skel_curv = self.marker_io.load_marker_curve(subj, takename)

    def read_skel(self, ind, cam):
        return self.cam_dict[cam].project_linear(self.skel_curv[ind, :, :].T.astype(np.float64))

    def get_frame_num(self):
        return self.skel_curv.shape[0]