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
        if ind >= skip and ret:
            frame_l.append(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (1920, 1080), cv2.INTER_LANCZOS4))

    cap.release()
    return np.mean(frame_l, axis=0) / 255.0


class VideoReader:
    def __init__(self, fname):
        self.cap = cv2.VideoCapture(fname)
        self.frame_ind = 0

    def get_max_frame(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def read_frame_ts(self, ind):
        if ind != self.frame_ind:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, ind)

        ts = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        _, frame = self.cap.read()
        frame = cv2.resize(frame[:, :, ::-1], (1920, 1080), cv2.INTER_LANCZOS4)
        self.frame_ind = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return frame, ts

    def close(self):
        self.cap.release()