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
    "tang": "20180907_dy_camparams.pkl", "ryan": "20180911_ryan_camparams.pkl"}

align_prog = "/home/liyanc/Desktop/Preprocess/align_time.py"
calib_prog = "/home/liyanc/Desktop/Preprocess/linear_regress_timing.py"

root_dir = "/home/liyanc/Desktop/raid/scratch2/pose/processing/staging"
subj, takename = input("subject name,take name(separated by , ) ").lower().strip().split(",")
day_subdir = input("Recording date")
marker_dir = "meta_mid/"
bvh_dir = "BVHmat/"
camparam_file = "meta_mid/cameras/{:}".format(subj2camparam[subj])
timecorr_file = "meta_mid/alignments/{:}_{:}_timecorr.pkl".format(subj, takename)
timeparam_file = "meta_mid/alignments/{:}_{:}_timeparams.pkl".format(subj, takename)
newcam_dir = "meta_mid/cameras/subj_take/"

print("Remember cameras that look incorrect!")
cmd = ["python3", align_prog, root_dir, "{:},{:}".format(subj, takename), day_subdir, marker_dir, bvh_dir,
        camparam_file, timecorr_file]
exe.run_command(cmd)

cmd = ["python3", calib_prog, root_dir, "{:},{:}".format(subj, takename), day_subdir, marker_dir, bvh_dir,
        camparam_file, timecorr_file, timeparam_file, newcam_dir]
exe.run_command(cmd)
