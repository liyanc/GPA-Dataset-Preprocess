"""
"""

__author__ = "Liyan Chen"

import numpy as np


def show_clicks_reporj_on_img(ax, img, clicks, reproj, cam):
    ax.imshow(img)
    ax.plot(clicks[:, 0], clicks[:, 1], "b+", label="Ground truth")
    ax.plot(reproj[:, 0], reproj[:, 1], "rx", label="Reprojection")
    ax.legend()
    ax.set_title("Camera {:}".format(cam))


def show_hist_reproj_err(ax, csolver, p_world, q_proj):
    ax.hist(csolver.projection_errs(p_world.T, q_proj.T), alpha=0.8)
    ax.set_title("Mean projerr: {:}".format(np.mean(csolver.projection_errs(p_world.T, q_proj.T))))
