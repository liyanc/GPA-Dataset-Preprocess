"""
"""

__author__ = "Liyan Chen"


#!/usr/bin/env python
from scipy.io import loadmat
from numpy import transpose
import skimage.io as sio
import numpy as np
import os
import sys
## the MPII format is: joint id (0 - r ankle, 1 - r knee, 2 - r hip, 3 - l hip, 4 - l knee, 5 - l ankle, 6 - pelvis, 7 - thorax, 8 - upper neck, 9 - head top, 10 - r wrist, 11 - r elbow, 12 - r shoulder, 13 - l shoulder, 14 - l elbow, 15 - l wrist), currently we define half head size as 0.5 * [head top - upper neck], other code use defaults 150 mm [MPI_INF_3DHP] (not sure how they calculate it out), or [0:50:200], for plotting curves [h36m paper]

def eval_PCKh_3d_func(pos_pred_src,pos_gt_src, jnt_visible, threshold='0.5', SC_BIAS = '0.6'):
    # 2958 is the number of person and 16 is the number of joints for one person
    #dataset_joints  # 1*16
    #jnt_missing   # 16*2958
    #pos_pred_src  # 16*2*2958
    #pos_gt_src # 16*2*2958
    # joints_visible binary matrix with 16*2958
    #jnt_visible = np.ones((16,2968))
    uv_error = pos_pred_src - pos_gt_src
    uv_err = np.linalg.norm(uv_error, axis=1)
    headsizes = pos_gt_src[8,:, :] - pos_gt_src[9,:, :]
    headsizes = np.linalg.norm(headsizes, axis=0)  # 1*2958
    headsizes *= SC_BIAS # 0.6
    #print(headsizes)
    scale = np.multiply(headsizes, np.ones((len(uv_err), 1)))  # 16*2958
    scale = scale + sys.float_info.epsilon
    scaled_uv_err = np.divide(uv_err, scale) # 16*2958
    scaled_uv_err = np.multiply(scaled_uv_err, jnt_visible)  #we assume all the 3d joints visible in our experiments
    #jnt_count = pos_gt_src.shape[0]* pos_gt_src.shape[2]
    jnt_count = np.sum(jnt_visible, axis=1)
    less_than_threshold = np.multiply((scaled_uv_err < threshold), jnt_visible)
    PCKh_3d = np.divide(100. * np.sum(less_than_threshold, axis=1), jnt_count)
    PCKh_3d = np.ma.array(PCKh_3d, mask=False)
    PCKh_3d.mask[6:8] = True
    print("Model,  Head,   Shoulder, Elbow,  Wrist,   Hip ,     Knee  , Ankle ,  Mean")
    print('{:s}   {:.2f}  {:.2f}     {:.2f}  {:.2f}   {:.2f}   {:.2f}   {:.2f}   {:.2f}'.format('pose_3d', PCKh_3d[9], 0.5 * (PCKh_3d[13] + PCKh_3d[12])\
        , 0.5 * (PCKh_3d[14] + PCKh_3d[11]),0.5 * (PCKh_3d[15] + PCKh_3d[10]), 0.5 * (PCKh_3d[3] + PCKh_3d[2]), 0.5 * (PCKh_3d[4] + PCKh_3d[1]) \
        , 0.5 * (PCKh_3d[5] + PCKh_3d[0]), np.mean(PCKh_3d)))
#!/usr/bin/env python
if __name__ == '__main__':
    dict = loadmat('detections_our_format.mat')  # from https://github.com/bearpaw/pytorch-pose/blob/master/evaluation/data/detections_our_format.mat
    jnt_missing = dict['jnt_missing'] # 16*2958
    pos_pred_src = dict['pos_pred_src']  # 16*2*2958
    pos_gt_src = dict['pos_gt_src']  # 16*2*2958
    jnt_visible = 1 - jnt_missing
    eval_PCKh_3d_func(pos_pred_src,pos_gt_src, jnt_visible, threshold=0.5, SC_BIAS = 0.6)