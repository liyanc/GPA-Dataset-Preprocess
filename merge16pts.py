"""
"""

__author__ = "Liyan Chen"

import scipy.io as sio
import numpy as np
import h5py
import os
import glob
J = 16
# pose-affordance to h36m batch_generate_imagedata
#inds = [1,25,26,27,30,31,32,3,6,7,8,18,19,20,10,11,12] - 1
inds = [0,24,25,26,29,30,31,2,5,6,7,17,18,19,9,10,11]
# in the original code
inds_2 = [3, 2, 1, 4, 5, 6, 0, 7, 8, 10, 16, 15, 14, 11, 12, 13]
#subject_list = [[1, 5, 6, 7, 8], [9, 11]]
#action_list = np.arange(2, 17)
#video_list = [[1,2,3,4,5,6,7,8,9,10], [11, 12, 13, 14]]
video_list = [[1,2,3,4,5,6,7,8,11,12], [9, 10, 13, 14]]
# zhe add
#np.delete(action_list, 8)
#subaction_list = np.arange(1, 3)
#camera_list = np.arange(1, 5)
#IMG_PATH = '/home/zwang15/pytorch-pose-hg-3d/images/'
IMG_PATH = '/home/wangzhe/PycharmProjects/pytorch-pose-hg-3d_zwdbh/data/pose_affordance/'
SAVE_PATH = '../../data/pose_affordance/'
annot_name = 'video_joints_7_fullpose.mat'

if not os.path.exists(SAVE_PATH):
  os.mkdir(SAVE_PATH)

id = []
joint_2d = []
joint_3d_mono = []
joint_2d_bnd = []
bbox = []
subjects = []
actions = []
subactions = []
cameras = []
istrain = []
videos = []
file_name = []
num = 0

for split in range(2):
  for video in video_list[split]:
          folder_name = '{:03d}'.format(video)
          print folder_name
          annot_file = IMG_PATH + folder_name + '/' + annot_name
          try:
            data = sio.loadmat(annot_file)
          except:
            print 'pass', folder_name
            continue
          n = data['filenames'].shape[1]
          print(n)
          #n = len(glob.glob1(IMG_PATH + folder_name + '/',"*.jpg"))
          #filenames = glob.glob1(IMG_PATH + folder_name + '/',"*.jpg")
          filenames = data['filenames']
          meta_Y2d_bnd_0 = data['j2d_bnd']#.reshape(17, 2, n)  #1925*2*34
          meta_Y2d_0 = data['j2d']
          meta_Y3d_mono_0 = data['j3d']*10 #.reshape(17, 3, n)  1604*34*3
          #print(meta_Y2d_bnd_0.shape)
          #print(meta_Y2d_0.shape)
          #print(meta_Y3d_mono_0.shape)
          meta_Y2d_bnd = meta_Y2d_bnd_0[:,:,inds]
          meta_Y2d = meta_Y2d_0[:,inds,:]
          meta_Y3d_mono = meta_Y3d_mono_0[:,inds,:]
          bboxx = data['bbox']  #.transpose(1, 0)
          for i in range(n):
            #for j in range(16):
            #  if meta_Y2d_bnd[i,0, j] < 0 or meta_Y2d_bnd[i,0, j]>223 or meta_Y2d_bnd[i,1, j] < 0 or meta_Y2d_bnd[i,1, j]>223:
            #    continue
            id.append(i + 1)
            joint_2d.append(meta_Y2d[i,inds_2,:])
            joint_2d_bnd.append(meta_Y2d_bnd[i,:, inds_2])
            joint_3d_mono.append(meta_Y3d_mono[i,inds_2, :])
            #print(filenames[0][2][0])
            #print(bboxx[i,:])
            bbox.append(bboxx[i,:])
            videos.append(video)
            file_name.append(str(filenames[0][i][0]))
            #print(file_name)
            #subjects.append(subject)
            #actions.append(action)
            #subactions.append(subaction)
            #cameras.append(camera)
            istrain.append(1 - split)
            num += 1

print 'num = ', num
h5name = SAVE_PATH + 'pose_affordance_fullpose.h5'
f = h5py.File(h5name, 'w')
f['id'] = id
f['joint_2d'] = joint_2d
f['joint_2d_bnd'] = joint_2d_bnd
f['joint_3d_mono'] = joint_3d_mono
f['bbox'] = bbox
f['videos'] = videos
f['file_name'] = file_name
#f['action'] = actions
#f['subaction'] = subactions
#f['camera'] = cameras
f['istrain'] = istrain
f.close()