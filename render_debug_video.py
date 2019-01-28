"""
"""

__author__ = "Liyan Chen"


import argparse
import FileIO as fio
import UI as ui

parser = argparse.ArgumentParser()
parser.add_argument("root_dir", type=str)
parser.add_argument("subj_takename_cam", type=str)
parser.add_argument("marker_dir", type=str)
parser.add_argument("bvh_dir", type=str)
parser.add_argument("md_dir", type=str)
parser.add_argument("camparam_dir", type=str)
parser.add_argument("timecorr_dir", type=str)
parser.add_argument("out_dir", type=str)
args = parser.parse_args()
apath = fio.ArgPathBuilder(args)

subj, takename, cam = args.subj_takename_cam.split(",")

render = ui.TakeRender(args.root_dir, args.camparam_dir, args.timecorr_dir, args.marker_dir, args.bvh_dir,
                       args.md_dir, subj, takename, cam)
render.render_single_thread(args.out_dir)


