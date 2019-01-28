"""
"""

__author__ = "Liyan Chen"


import FileIO as fio
import UI as ui
import Execution as exe

rt_path = "/media/10T/GPA_raw/processing/staging"
bvh_dir = "resolve_bvh2mat"
marker_dir = "meta_mid"
md_dir = "mdmap"
camparam_dir = "meta_mid/cameras/subj_take/"
timecorr_dir = "meta_mid/alignments"
out_dir = "/home/cvlab/theta_scratch2/GPA1.1/video"

time_io = fio.TimeParamDir("{:}/{:}".format(rt_path, timecorr_dir))

commands = []
for s, r in time_io.subj_take_table.items():
    for t in r:
        for cam in ["00", "03", "01", "04", "02"]:
            cmd = ["python3", "render_debug_video.py", rt_path, "{:},{:},{:}".format(s, t, cam), marker_dir, bvh_dir,
                   md_dir, camparam_dir, timecorr_dir, out_dir]
        commands.append(cmd)
exe.bash_line_pool(commands, pool_size=2, sleep_time=1.5)