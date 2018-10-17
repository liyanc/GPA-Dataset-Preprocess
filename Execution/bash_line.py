"""
"""

__author__ = "Liyan Chen"


import multiprocessing as mp
import subprocess as sp
import time


def bash_line_pool(cmds, pool_size=mp.cpu_count(), sleep_time=0.05):
    num_task = len(cmds)
    proc_list = []
    comp_list = []

    while len(comp_list) < num_task:
        while len(proc_list) < pool_size and len(cmds) > 0:
            cmd = cmds.pop(0)
            proc_list.append(sp.Popen(cmd, stdout=sp.PIPE))

        for ind in range(len(proc_list)):
            if proc_list[ind].poll() is not None:
                proc = proc_list.pop(ind)
                comp_list.append(proc)
                break
            else:
                time.sleep(sleep_time)

    cmd_res = []
    for proc in comp_list:
        cmd_res.append((proc.args, proc.stdout.read()))
        proc.stdout.close()

    return cmd_res


def print_execution_result(cmd_res):
    for res in cmd_res:
        print(" ".join(res[0]) + " :\n" + str(res[1]))


def cmd_mkdir(dir):
    return [["mkdir", str(dir)]]


def extract_tar(tar_list, dest_dir):
    return [["tar", "-xzf", f, "-C", dest_dir + "/"] for f in tar_list]


def copy_list(src_list, dest_dir):
    return [["cp", s, dest_dir + "/"] for s in src_list]