"""
"""

__author__ = "Liyan Chen"


import cv2
import numpy as np


def video_mean_frame(fname, skip=2, length=50):
    frame_l = []
    cap = cv2.VideoCapture(fname)
    for ind in range(length):
        if not cap.isOpened(): break
        ret, frame = cap.read()
        if ind >= skip and ret: frame_l.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    cap.release()
    return np.mean(frame_l, axis=0) / 255.0