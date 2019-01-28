"""
"""

__author__ = "Liyan Chen"

import numpy as np


def occl_test(pts_3d, imgpts, md_channel, objcam, undetermined=0):
    md_layer1 = md_channel[:, :, 0] / 10  # divide by 10 to make it as cm
    pts_occlusion = []
    cam_pts = objcam.camera_coordinate(pts_3d).T
    for ind in range(pts_3d.shape[0]):
        pt = imgpts[ind, :]
        cam_3d = cam_pts[ind, :]
        if np.any(np.isnan(pt)):
            pts_occlusion.append(undetermined)
        elif int(pt[1]) not in range(1080) or int(pt[0]) not in range(1920):
            pts_occlusion.append(undetermined)
        elif cam_3d[2] > md_layer1[int(pt[1]), int(pt[0])]:
            pts_occlusion.append(1)
        else:
            pts_occlusion.append(0)
    return np.array(pts_occlusion)
