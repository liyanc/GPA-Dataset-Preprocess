"""
"""

__author__ = "Liyan Chen"

import cv2
import numpy as np


class CameraSolverNonlinear:
    def __init__(self, init_f=(1125.0, 1125.0), init_c=(500.0, 500.0), img_size=(1000, 1000)):
        self.init_f = init_f
        self.init_c = init_c
        self.img_size = img_size

    def solve(self, p_world, q_truth, iterations=300, term_epsilon=1e-3):
        f = np.random.normal(self.init_f, 40.0, [2]).astype(np.float64)
        c = np.random.normal(self.init_c, 20.0, [2]).astype(np.float64)

        init_cam = np.array([
            [f[0], 0, c[0]],
            [0, f[1], c[1]],
            [0,    0,   1]])
        flags = cv2.CALIB_USE_INTRINSIC_GUESS | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K6
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, iterations, term_epsilon)
        retval, cam, dist, rvecs, tvecs = cv2.calibrateCamera(
            [p_world.T.astype(np.float32)], [q_truth.T.astype(np.float32)], self.img_size, init_cam, None, flags=flags,
            criteria=crit)

        self.cam = cam
        self.dist = dist
        self.theta = rvecs[0]
        self.t = tvecs[0]

        return self.cam, self.dist, self.theta, self.t

    def projection_errs(self, p_world, q_truth):
        proj_pts, _ = cv2.projectPoints(p_world.T, self.theta, self.t, self.cam, self.dist)
        return np.sqrt(np.sum((q_truth.T - proj_pts[:, 0, :]) ** 2, axis=1))

    def undistort_pts(self, dist_p):
        undist = cv2.undistortPoints(np.expand_dims(dist_p.T, 0), self.cam, self.dist, np.identity(3), self.cam)
        return undist[0, ...]

    def undistort_img(self, img):
        undist = cv2.undistort(img, self.cam, self.dist)
        return undist

    def project_linear(self, p_world):
        proj_pts, _ = cv2.projectPoints(p_world.T, self.theta, self.t, self.cam, None)
        return proj_pts[:, 0, :]

    def camera_coordinate(self, p_world):
        R = cv2.Rodrigues(self.theta)[0]
        return np.matmul(R, p_world.T) + self.t

    def world_coordinate_by_z_imgpt(self, imgpt, z):
        R = cv2.Rodrigues(self.theta)[0]
        K = self.cam
        cam_pts = np.concatenate(
            [(imgpt - K[:2, 2]) / K.diagonal()[:2], np.ones((imgpt.shape[0], 1))], 1) * z[:, np.newaxis]
        return np.matmul(R.T, cam_pts.T - self.t).T