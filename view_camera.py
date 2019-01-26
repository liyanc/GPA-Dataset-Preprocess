"""
"""

__author__ = "Liyan Chen"

import Execution as exe

subj2camparam = {
    "liyan": "20180831_liyan_camparams.pkl", "lisi": "20180901_lisi_camparams.pkl",
    "deying": "20180901_lisi_camparams.pkl", "haoyu": "20180902_haoyu_camparams.pkl",
    "shau": "20180902_haoyu_camparams.pkl", "jingwen": "20180903_jingwen_camparams.pkl",
    "zhe": "20180903_jingwen_camparams.pkl", "xie": "20180906_yan_camparams.pkl",
    "yan": "20180906_yan_camparams.pkl", "dy": "20180907_dy_camparams.pkl",
    "tang": "20180907_tang_camparams.pkl", "ryan": "20180911_ryan_camparams.pkl",
    "lin": "20180911_ryan_camparams.pkl"}

align_prog = "/home/liyanc/Desktop/Preprocess/align_time.py"
calib_prog = "/home/liyanc/Desktop/Preprocess/linear_regress_timing.py"
replay_prog = "/home/liyanc/Desktop/Preprocess/replay_camera.py"

root_dir = "/home/liyanc/Desktop/raid/scratch2/pose/processing/staging"
subj, takename = input("subject name,take name(separated by , ): ").lower().strip().split(",")
day_subdir = input("Recording date: ")
marker_dir = "meta_mid/"
bvh_dir = "resolve_bvh2mat/"
camparam_file = "meta_mid/cameras/{:}".format(subj2camparam[subj])
timecorr_file = "meta_mid/alignments/{:}_{:}_timecorr.pkl".format(subj, takename)
timeparam_file = "meta_mid/alignments/{:}_{:}_timeparams.pkl".format(subj, takename)
newcam_dir = "meta_mid/cameras/subj_take/"
newcam_param = "meta_mid/cameras/subj_take/{:}_{:}_camparams.pkl".format(subj, takename)
pnp_param = "meta_mid/cameras/solvepnp_params/{:}_{:}_camparams.pkl".format(subj, takename)

opt_params = [camparam_file, newcam_param, pnp_param]
cam_opt = int(input(
    "Camera options: 0: from static geometry; 1: from 1st calibration pass; 2: from solvepnp; 3: input: ").strip())
if cam_opt in range(0, 3):
    cam_loadfile = opt_params[cam_opt]
elif cam_opt == 3:
    cam_loadfile = input("Type camera parameter file: ")
else:
    raise ValueError("illegal option {:}".format(cam_opt))

cmd = ["python3", replay_prog, root_dir, "{:},{:}".format(subj, takename), day_subdir, marker_dir, bvh_dir,
       cam_loadfile, timecorr_file]
exe.run_command(cmd)