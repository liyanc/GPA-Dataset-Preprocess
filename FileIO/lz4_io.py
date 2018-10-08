"""
"""

__author__ = "Liyan Chen"

import cv2
import glob
import numpy as np
import ctypes
from ctypes import cdll

lz4 = cdll.LoadLibrary("liblz4.so")


def imread_from_lz4(fname):
    with open(fname, "rb") as f:
        contents = f.read()
    bufsize = 6221000
    dst = ctypes.create_string_buffer(bufsize)
    lz4.LZ4_decompress_safe(contents, dst, len(contents), bufsize)
    return cv2.imdecode(np.frombuffer(dst.raw), cv2.IMREAD_ANYCOLOR)


def lz4_mean_img(f_list):
    return np.mean([imread_from_lz4(f) for f in f_list], axis=0) / 255.0


def list_img_cam(imgdir, cam, skip=2, length=50):
    cam_file = sorted(
        [f for f in glob.glob(imgdir + "/*.bmp.lz4") if f.split("/")[-1].split("-")[0] == cam],
        key=lambda f: int(f.split("/")[-1].split("-")[1]))
    return cam_file[skip: length]
