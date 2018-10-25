"""
"""

__author__ = "Liyan Chen"

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import widgets as wdgt


def show_clicks_reporj_on_img(ax, img, clicks, reproj, cam):
    ax.imshow(img)
    ax.plot(clicks[:, 0], clicks[:, 1], "b+", label="Ground truth")
    ax.plot(reproj[:, 0], reproj[:, 1], "rx", label="Reprojection")
    ax.legend()
    ax.set_title("Camera {:}".format(cam))


def show_hist_reproj_err(ax, csolver, p_world, q_proj):
    ax.hist(csolver.projection_errs(p_world.T, q_proj.T), alpha=0.8)
    ax.set_title("Mean projerr: {:}".format(np.mean(csolver.projection_errs(p_world.T, q_proj.T))))


def show_proj_on_img(ax, img, proj):
    ax.imshow(img)
    ax.plot(proj[:, 0], proj[:, 1], "b+", label="Ground truth")


class ImgWithPtsRender:
    def __init__(self, ax, init_img, init_pts):
        ax.grid(False)
        self.img_ref = ax.imshow(init_img)
        self.pts_ref, = ax.plot(init_pts[:, 0], init_pts[:, 1], "b+", label="Ground Truth")

    def update_img(self, img):
        self.img_ref.set_data(img)

    def update_pts(self, pts):
        self.pts_ref.set_xdata(pts[:, 0])
        self.pts_ref.set_ydata(pts[:, 1])

    def update_img_pts(self, img, pts):
        self.img_ref.set_data(img)
        self.pts_ref.set_xdata(pts[:, 0])
        self.pts_ref.set_ydata(pts[:, 1])


class TimeAlignmentWindow:
    def __init__(self, cam, img_reader, mkr_reader, base_offset=0, render_int=10):
        # Initialize states
        self.render_int = render_int
        self.cam = cam
        self.img_reader = img_reader
        self.mkr_reader = mkr_reader
        self.timer_running = False
        self.allowed_update_offset = True
        self.frame_int = 26.66666666666667 if cam in self.img_reader.kinect_cam else 33.3333333333333

        self.offset = base_offset
        init_img, self.cam_t0 = img_reader.read_img_ts(0, cam)
        self.cam_ts = self.cam_t0
        self.cam_ind, max_cam_ind = 0, img_reader.get_frame_num_for_cam(cam) - 1
        self.skel_ind, max_skel_ind = self.get_mocap_ind(), mkr_reader.get_frame_num() - 1
        init_pts = mkr_reader.read_skel(int(round(self.skel_ind)), cam)

        # Initialize GUI
        self.fig = plt.figure()
        self.imgax = plt.subplot(111)
        plt.subplots_adjust(bottom=0.15, top=1.0, left=0.05, right=0.95)
        self.cslider_ax = plt.axes([0.1, 0.1, 0.8, 0.03])
        self.sslider_ax = plt.axes([0.1, 0.05, 0.8, 0.03])
        self.cam_slider = wdgt.Slider(self.cslider_ax, "Camera Time", 0, max_cam_ind, self.cam_ind, valstep=1.0)
        self.skel_slider = wdgt.Slider(self.sslider_ax, "Skeleton Time", 0, max_skel_ind, self.skel_ind, valstep=1.0)
        self.timer = self.fig.canvas.new_timer(interval=render_int)
        self.img_pts_render = ImgWithPtsRender(self.imgax, init_img, init_pts)

        self.register_callback()

    def get_mocap_ind(self):
        factor = self.img_reader.get_equiv_mocap_frame(self.cam)
        return (self.cam_ts - self.cam_t0) / self.frame_int * factor + self.offset

    def update_offset(self):
        if self.allowed_update_offset:
            factor = self.img_reader.get_equiv_mocap_frame(self.cam)
            self.offset = self.skel_ind - (self.cam_ts - self.cam_t0) / self.frame_int * factor

    def update_cam_ind(self, new_cam_ind):
        self.cam_ind = new_cam_ind
        img, self.cam_ts = self.img_reader.read_img_ts(self.cam_ind, self.cam)
        self.update_offset()
        self.img_pts_render.update_img(img)

    def update_skel_ind(self, new_pts_ind):
        self.skel_ind = new_pts_ind
        self.update_offset()
        self.img_pts_render.update_pts(self.mkr_reader.read_skel(int(round(self.skel_ind)), self.cam))

    def on_cam_slider(self, val):
        self.update_cam_ind(int(self.cam_slider.val))

    def on_skel_slider(self, val):
        self.update_skel_ind(self.skel_slider.val)

    def on_wheel(self, event):
        self.allowed_update_offset = True
        if event.button == "up":
            self.skel_ind -= 1
        elif event.button == "down":
            self.skel_ind += 1

        self.skel_slider.set_val(self.skel_ind)
        plt.draw()

    def on_key(self, event):
        if event.key == " ":
            self.allowed_update_offset = False
            if self.timer_running:
                self.timer.stop()
            else:
                self.timer.start(interval=self.render_int)

            self.timer_running = not self.timer_running

    def on_timer(self, event):
        self.allowed_update_offset = False
        self.cam_ind += 1
        self.cam_slider.set_val(self.cam_ind)
        self.skel_ind = self.get_mocap_ind()
        self.skel_slider.set_val(self.skel_ind)
        self.allowed_update_offset = True

    def register_callback(self):
        self.cam_slider.on_changed(self.on_cam_slider)
        self.skel_slider.on_changed(self.on_skel_slider)
        self.timer.add_callback(self.on_timer, None)
        self.fig.canvas.mpl_connect("scroll_event", self.on_wheel)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

    def run(self):
        plt.show()
        if self.cam not in self.img_reader.kinect_cam:
            self.img_reader.close(self.cam)
        return self.offset