"""
"""

__author__ = "Liyan Chen"

import argparse
import glob
import Execution as ex

parser = argparse.ArgumentParser()
parser.add_argument("source_dir", type=str)
parser.add_argument("day_list", type=str)
parser.add_argument("dest_dir", type=str)
args = parser.parse_args()

days = args.day_list.split(",")

for day in days:

    cmds = ex.cmd_mkdir("{:}/{:}".format(args.dest_dir, day))
    ex.print_execution_result(ex.bash_line_pool(cmds))

    cmds = ex.cmd_mkdir("{:}/{:}/camera3".format(args.dest_dir, day)) + \
           ex.cmd_mkdir("{:}/{:}/camera4".format(args.dest_dir, day))
    ex.print_execution_result(ex.bash_line_pool(cmds))

    tar_list = glob.glob("{:}/{:}/*.tar.gz".format(args.source_dir, day))
    cmds = ex.extract_tar(tar_list, "{:}/{:}".format(args.dest_dir, day))

    for cam in ["camera3", "camera4"]:
        mp4_list = glob.glob("{:}/{:}/{:}/*.MP4".format(args.source_dir, day, cam))
        cmds += ex.copy_list(mp4_list, "{:}/{:}/{:}/".format(args.dest_dir, day, cam))
    ex.print_execution_result(ex.bash_line_pool(cmds, 1))