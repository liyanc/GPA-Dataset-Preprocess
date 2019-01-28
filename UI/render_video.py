"""
"""

__author__ = "Liyan Chen"

import cv2
import os
import numpy as np

import FileIO as fio
import Process as proc
import Specifications as spec


def drawline(img, pt1, pt2, color, thickness=1, style='dotted', gap=20):
    dist = ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** .5
    pts = []
    for i in np.arange(0, dist, gap):
        r = i / dist
        x = int((pt1[0] * (1 - r) + pt2[0] * r) + .5)
        y = int((pt1[1] * (1 - r) + pt2[1] * r) + .5)
        p = (x, y)
        pts.append(p)

    if style == 'dotted':
        for p in pts:
            cv2.circle(img, p, thickness, color, -1)
    else:
        s = pts[0]
        e = pts[0]
        i = 0
        for p in pts:
            s = e
            e = p
            if i % 2 == 1:
                cv2.line(img, s, e, color, thickness)
            i += 1
    return img


def plot_linkage(img, joints, occl, copy=True):
    plt_img = np.copy(img) if copy else img
    if ~np.any(np.isnan(joints)):
        for link in spec.linkage:
            pts = joints[link, :]
            e_ori = list(filter(lambda x: link[1] in x[1], enumerate(spec.orientation)))[0][0]
            s_ori = list(filter(lambda x: link[0] in x[1], enumerate(spec.orientation)))[0][0]
            e_color, s_color = list(spec.ori2color[x] for x in (e_ori, s_ori))
            if occl[link[0]] == 1 or occl[link[1]] == 1:
                plt_img = drawline(plt_img, tuple(pts[0, :].astype(int)), tuple(pts[1, :].astype(int)),
                                   e_color, 3, gap=12)
            else:
                plt_img = cv2.line(plt_img, tuple(pts[0, :].astype(int)), tuple(pts[1, :].astype(int)),
                                   e_color, 2, cv2.LINE_AA)
        for i in range(34):
            if occl[i] == 1:
                plt_img = cv2.circle(plt_img, tuple(joints[i, :].astype(int)), 8, spec.joint2color[i], 3)
            else:
                plt_img = cv2.circle(plt_img, tuple(joints[i, :].astype(int)), 6, spec.joint2color[i], cv2.FILLED)

    return plt_img


def plot_marker(img, markers, occl, copy=True, size=8):
    plt_img = np.copy(img) if copy else img
    plt_mkr = markers[~np.any(np.isnan(markers), axis=1)]
    for i in range(plt_mkr.shape[0]):
        color = (121, 142, 150) if occl[i] == 1 else (125, 179, 210)
        plt_img = cv2.drawMarker(plt_img, tuple(plt_mkr[i, :].astype(int)), color,
                                 cv2.MARKER_TILTED_CROSS, size, 2, cv2.LINE_AA)
    return plt_img


def render_l_img(img, markers, joints, marker_occl, joint_occl):
    plt_img = plot_marker(img, markers, marker_occl)
    plt_img = plot_linkage(plt_img, joints, joint_occl, False)
    return proc.aa_resize(plt_img, (0.64, 0.64), lp_filter=False)


def render_s_img(img, markers, joints, markers_3d, joints_3d, marker_occl, joint_occl, camobj, supp_pts, size=691):
    padding = 0.04 * size
    r_img, new_cam = proc.resize_pad_crop_img_with_camparams(img, supp_pts, camobj.dump_params(), size, padding)
    camproj = proc.param2camproj(new_cam)
    new_joints = camproj.project_linear(joints_3d.T.astype(np.float32))
    new_markers = camproj.project_linear(markers_3d.T.astype(np.float32))

    plt_img = plot_marker(r_img, new_markers, marker_occl, size=12)
    return plot_linkage(plt_img, new_joints, joint_occl, False)


def text_render(table, padding=15, char_size=30, ver_size=19, scale=1):
    text_strip = np.zeros((389, 1920, 3), np.uint8)
    col = len(table[0])
    max_len = [36] * col
    for c in range(col):
        for line in table:
            if isinstance(line, list):
                max_len[c] = max(max_len[c], len(line[c]))
    for ln, line in enumerate(table):
        btm = (ln + 1) * char_size * scale + padding * ln
        if isinstance(line, list):
            for cn, cell in enumerate(line):
                cell_offset = 0 if cn == 0 else max_len[cn - 1] * ver_size * scale
                cell_padding = (cn + 1) * padding
                left = cell_offset + cell_padding
                text_strip = cv2.putText(text_strip, cell, (left, btm), cv2.FONT_HERSHEY_COMPLEX, scale,
                                         (255, 255, 255), 2, cv2.FILLED)
        else:
            text_strip = cv2.putText(text_strip, line, (padding, btm), cv2.FONT_HERSHEY_COMPLEX, scale, (255, 255, 255),
                                     2, cv2.FILLED)

    return text_strip


def cal_id(subj, takename, cam):
    return "ID: {:} | {:} | Camera{:}".format(subj, takename, cam)


def cal_setmembership():
    return "Set: {Placeholder}"


def cal_frame(frame, frame_len):
    return "Frame: {:05}/{:05}".format(frame, frame_len)


def cal_ts(mocap_t_raw):
    return "Timestamp: {:09.2f}".format(mocap_t_raw)


def cal_stability():
    return "Stability: {Placeholder}"


def cal_markers(markers):
    return "# Markers: {:02}".format(np.sum(~np.any(np.isnan(markers), axis=1)))


def cal_vis_markers(markers_occl):
    return "Invis Markers: {:02}".format(np.sum(markers_occl))


def cal_vis_joints(joints_occl):
    return "Invis Joints: {:02}".format(np.sum(joints_occl))


def cal_bone_length(joints_3d, linkage):
    length = []
    for link in linkage:
        s, e = joints_3d[link, :]
        length.append(np.sqrt(np.sum((s - e) ** 2)))
    return "Bone length: " + " | ".join("{:}%:{:.2f}".format(p, n) for (n, p) in zip(
        np.percentile(length, [25, 50, 75]), [25, 50, 75])) + " | mean: {:.2f} | max: {:.2f}".format(
        np.mean(length), np.max(length))


def cal_velocity(joints_3d, pre_joints_3d):
    dis = np.sqrt(np.sum((pre_joints_3d - joints_3d) ** 2, axis=1))
    means = [np.mean(dis[spec.arms]), np.mean(dis[spec.legs]), np.mean(dis)]
    percentile = list(np.percentile(dis, [25, 50, 75]))
    ratio = [means[1] / means[0]]
    return "Velocity: " + " | ".join("{:}:{:.2f}".format(t, n) for (n, t) in zip(means + ratio + percentile,
                                                                                 ["arms", "legs", "body",
                                                                                  "leg/arm_ratio", "25%", "50%",
                                                                                  "75%"]))


def gen_text(
        subj, takename, cam, t_num, total_f, mocap_t_raw, joints, joints_3d, pre_joints_3d, joint_occl,
        linkage, markers, marker_occl):
    table = [[cal_id(subj, takename, cam), cal_stability()],
             [cal_setmembership(), cal_markers(markers)],
             [cal_frame(t_num, total_f), cal_vis_markers(marker_occl)],
             [cal_ts(mocap_t_raw), cal_vis_joints(joint_occl)],
             cal_bone_length(joints_3d, linkage),
             cal_velocity(joints_3d, pre_joints_3d)
             ]
    return text_render(table)


class TakeRender:
    def __init__(self, rt_path, camparam_dir, timecorr_dir, marker_dir, bvh_dir, md_dir, subj, takename, cam):
        self.cam_io = fio.CamParamDir(fio.concat_path(rt_path, camparam_dir))
        self.time_io = fio.TimeParamDir("{:}/{:}".format(rt_path, timecorr_dir))

        self.cam_dict = fio.load_cam(self.cam_io.get_camparam_file(subj, takename))
        self.imgdir_io = fio.ImgDirIO(fio.concat_path(rt_path, spec.subj2day[subj]), subj, takename)
        self.viddir_io = fio.VideoDirIO(fio.concat_path(rt_path, spec.subj2day[subj]), subj, takename)
        self.marker_io = fio.MarkerDirIO(fio.concat_path(rt_path, marker_dir))
        self.joint_io = fio.BVHDirIO(fio.concat_path(rt_path, bvh_dir))
        self.img_reader = fio.ImgProjReader(self.cam_dict, self.imgdir_io, self.viddir_io)
        self.mkr_reader = fio.MarkerSkeletonProjReader(self.cam_dict, self.marker_io, self.joint_io, subj, takename)
        self.md_reader = fio.MDMapLoader(fio.concat_path(rt_path, md_dir), subj, takename, cam)
        self.subj, self.takename, self.cam = subj, takename, cam

        self.frame_num = self.img_reader.get_frame_num_for_cam(cam)
        self.frame_list = self.img_reader.get_frame_list_for_cam(cam)

    def render_frame(self, t_num, total_f, cam_t, prev_cam_t, imgraw):
        img = self.img_reader.undistort_raw(imgraw, self.cam)
        mocap_t_raw = self.time_io.map_cam_timestamp_2mocap(self.subj, self.takename, self.cam, cam_t)
        mocap_t = int(round(mocap_t_raw))
        pre_mocap_t = int(round(self.time_io.map_cam_timestamp_2mocap(self.subj, self.takename, self.cam, prev_cam_t)))
        joints, markers = self.mkr_reader.read_joint(mocap_t, self.cam), self.mkr_reader.read_skel(mocap_t, self.cam)
        joints_3d, markers_3d = self.mkr_reader.read_raw_joint(mocap_t), self.mkr_reader.read_raw_skel(mocap_t)
        pre_joints_3d = self.mkr_reader.read_raw_joint(pre_mocap_t)

        supp_pts = proc.valid_supp_pts(markers_3d, joints_3d)

        joint_occl = proc.occl_test(joints_3d, joints, self.md_reader.md_channel, self.cam_dict[self.cam])
        marker_occl = proc.occl_test(markers_3d, markers, self.md_reader.md_channel, self.cam_dict[self.cam])

        l_img = render_l_img(img, markers, joints, marker_occl, joint_occl)
        z_img = render_s_img(
            img, markers, joints, markers_3d, joints_3d, marker_occl, joint_occl, self.cam_dict[self.cam], supp_pts)
        img_strip = np.concatenate([l_img, z_img], axis=1)

        text_strip = gen_text(
            self.subj, self.takename, self.cam, t_num, total_f, mocap_t_raw, joints, joints_3d, pre_joints_3d,
            joint_occl, spec.linkage, markers, marker_occl)
        rendered_frame = np.concatenate([img_strip, text_strip], axis=0)
        return rendered_frame

    def get_max_len(self):
        return self.frame_num

    def get_frame_list(self):
        return self.frame_list

    def gen_render_src(self):
        prev_cam_t = None
        for t_num, e in enumerate(self.frame_list):
            imgraw, cam_t = self.img_reader.read_img_ts(t_num, self.cam, False)
            if prev_cam_t is None:
                prev_cam_t = cam_t

            yield t_num, self.frame_num, cam_t, prev_cam_t, imgraw
            prev_cam_t = cam_t

    def render_single_thread(self, out_dir):
        out_file = "{:}/{:}_{:}_cam{:}_debug.mp4".format(out_dir, self.subj, self.takename, self.cam)
        if not os.path.exists(out_file):
            fourcc = cv2.VideoWriter_fourcc(*'MP4V')
            v_writer = cv2.VideoWriter(
                "{:}/{:}_{:}_cam{:}_debug.mp4".format(out_dir, self.subj, self.takename, self.cam),
                fourcc, 30.0, (1920, 1080))
            for tp in self.gen_render_src():
                frame = self.render_frame(*tp)
                v_writer.write(frame[..., ::-1])
            v_writer.release()
        print("Render Finished for {:}|{:}|{:}".format(self.subj, self.takename, self.cam))
