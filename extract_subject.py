"""
"""

__author__ = "Liyan Chen"

import argparse
import glob
import Execution as ex

parser = argparse.ArgumentParser()
parser.add_argument("source_dir", type=str)
parser.add_argument("day", type=str)
parser.add_argument("dest_dir", type=str)
args = parser.parse_args()

cmds = ex.cmd_mkdir("{:}/{:}".format(args.dest_dir, args.day))
ex.print_execution_result(ex.bash_line_pool(cmds))

cmds = ex.cmd_mkdir("{:}/{:}/camera3".format(args.dest_dir, args.day)) + \
       ex.cmd_mkdir("{:}/{:}/camera4".format(args.dest_dir, args.day))
ex.print_execution_result(ex.bash_line_pool(cmds))

tar_list = glob.glob("{:}/{:}/*.tar.gz".format(args.source_dir, args.day))
cmds = ex.extract_tar(tar_list, "{:}/{:}".format(args.dest_dir, args.day))

for cam in ["camera3", "camera4"]:
    mp4_list = glob.glob("{:}/{:}/{:}/*.MP4".format(args.source_dir, args.day, cam))
    cmds += ex.copy_list(mp4_list, "{:}/{:}/{:}/".format(args.dest_dir, args.day, cam))
ex.print_execution_result(ex.bash_line_pool(cmds, 1))