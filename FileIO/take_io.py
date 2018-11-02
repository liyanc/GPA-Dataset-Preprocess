"""
"""

__author__ = "Liyan Chen"

import glob
import os
import re
import csv
import FileIO as fio
import numpy as np
import scipy.io as sio
import Camera as camsolve
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
            sub = "deying" if sub == "deyingi" else sub
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


class TimeParamDir:

    def __init__(self, dir_path):
        self.subj_take_table = defaultdict(dict)
        self.params_subj_take_table = defaultdict(dict)
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")
        for f in glob.glob("{:}/*timecorr.pkl".format(dir_path)):
            fname = os.path.basename(f)
            sub = fname.split("_")[0]
            take = ptn.search(fname).group(0)
            self.subj_take_table[sub][take] = f

            corr = fio.load_pkl(f)
            timeparam_dict = dict(
                (cam, camsolve.ransac_linear_regress(v)) for (cam, v) in corr.items() if
                (sub, take, cam) not in CamParamDir.block_list)
            self.params_subj_take_table[sub][take] = timeparam_dict

    def get_timecorr(self, subj, takename):
        return self.subj_take_table[subj][takename]

    def get_timeparam(self, subj, takename):
        return self.params_subj_take_table[subj][takename]

    def map_cam_timestamp_2mocap(self, subj, takename, cam, timestamp):
        scale,  offset, _, _ = self.params_subj_take_table[subj][takename][cam]
        return timestamp * scale[0] + offset


class CamParamDir:
    block_list = [
        ("liyan", "action_00", "04"), ("liyan", "zw_static_02", "04"), ("haoyu", "action_00", "03"),
        ("haoyu", "action_01", "03"), ("haoyu", "zw_static_03", "03"), ("haoyu", "zw_static_03", "04"),
        ("jingwen", "motion_00", "03"), ("jingwen", "motion_02", "03"), ("yan", "zw_static_01", "04")]

    def __init__(self, dir_path):
        self.subj_take_table = defaultdict(dict)
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")
        for f in glob.glob("{:}/*_camparams.pkl".format(dir_path)):
            fname = os.path.basename(f)
            sub = fname.split("_")[0]
            take = ptn.search(fname).group(0)
            self.subj_take_table[sub][take] = f

    def get_camparam_file(self, subj, takename):
        return self.subj_take_table[subj][takename]

    def is_blocklisted(self, subj, takename, cam):
        return (subj, takename, cam) in self.block_list


class BVHDirIO:
    sub_ind = [0, 24, 25, 26, 29, 30, 31, 2, 5, 6, 7, 17, 18, 19, 9, 10, 11]

    def __init__(self, rt_path):
        self.subj_take_table = defaultdict(dict)
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")

        csv_fname = "{:}/discarded_frames.csv".format(rt_path)
        with open(csv_fname) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row[1]) > 1 and ptn.search(row[1]) is not None:
                    _, fname, is_test, is_discarded, start, end = row[:6]
                    if is_discarded == "FALSE":
                        sub = fname.split("_")[0]
                        take = ptn.search(fname).group(0)
                        sub = "deying" if sub == "deyingi" else sub

                        remove_list = []
                        for pair in row[6:]:
                            try:
                                b, e = pair.split("-")
                            except ValueError:
                                pass
                            else:
                                b, e = int(b), int(e)
                                remove_list.append((b, e))
                        self.subj_take_table[sub][take] = {
                            "is_test": is_test == "TRUE", "is_discarded": is_discarded == "TRUE",
                            "start": int(start.replace(",", "")),
                            "end": int(end.replace(",", "")) if len(end) > 1 else None, "remove": remove_list}

        for f in glob.glob("{:}/*.mat".format(rt_path)):
            fname = os.path.basename(f)
            sub = fname.split("_")[0]
            take = ptn.search(fname).group(0)
            sub = "deying" if sub == "deyingi" else sub
            try:
                self.subj_take_table[sub][take]["file"] = f
            except KeyError:
                pass

    def load_joint_curve(self, subj, take):
        joints = sio.loadmat(self.subj_take_table[subj][take]["file"])["xyz_c"].astype(np.float64)
        start = self.subj_take_table[subj][take]["start"]

        pre_pad = np.zeros((start - 1, 34, 3), dtype=np.float64) - np.nan
        adj_joints = np.concatenate((pre_pad, joints))
        for b, e in self.subj_take_table[subj][take]["remove"]:
            adj_joints[b:(e + 1), :, :] = np.nan
        return adj_joints * 2.54  # Convert from inch to cm


class VideoDirIO:
    def __init__(self, rt_path, assigned_subj, assigned_take):
        self.cam_subj_take_file = {"03": defaultdict(dict), "04": defaultdict(dict)}
        self.cam_reader = {}
        ptn = re.compile("(action_\d{2})|(motion_\d{2})|(zw_static_\d{2})")
        for cam_name, cam in [("camera3", "03"), ("camera4", "04")]:
            if (assigned_subj, assigned_take, cam) not in CamParamDir.block_list:
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

    def read_cam_ts(self, cam):
        max_frame = self.cam_reader[cam].get_max_frame()
        return list(x * 33.36666666666667 for x in range(max_frame))

    def get_max_frame(self, cam):
        return self.cam_reader[cam].get_max_frame()

    def close(self, cam):
        self.cam_reader[cam].close()


class ImgProjReader:
    equiv_mocap_frame = {"00": 4, "01": 4, "02": 4, "03": 4, "04": 4}
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


class MarkerSkeletonProjReader:
    def __init__(self, cam_dict, marker_io, joint_io, subj, takename):
        self.cam_dict = cam_dict
        self.marker_io = marker_io
        self.joint_io = joint_io
        self.skel_curv = self.marker_io.load_marker_curve(subj, takename)
        self.joint_curv = self.joint_io.load_joint_curve(subj, takename)

    def read_raw_skel(self, ind):
        return self.skel_curv[ind, :]

    def read_raw_joint(self, ind):
        return self.joint_curv[ind, :]

    def read_skel(self, ind, cam):
        return self.cam_dict[cam].project_linear(self.skel_curv[ind, :, :].T.astype(np.float64))

    def read_joint(self, ind, cam):
        if ind >= self.joint_curv.shape[0] or ind < 0:
            return np.zeros((34, 3), np.float64) + np.nan
        else:
            return self.cam_dict[cam].project_linear(self.joint_curv[ind, :, :].T.astype(np.float64))

    def get_frame_num(self):
        return self.skel_curv.shape[0]

    def get_joint_frame_num(self):
        return self.joint_curv.shape[0]
