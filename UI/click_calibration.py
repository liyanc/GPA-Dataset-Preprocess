"""
"""

__author__ = "Liyan Chen"

from matplotlib import pyplot as plt
from matplotlib import patches as ptch


def get_marker_id(img, cam, unlabeled_dict, clicks=0, radius=6, alpha=0.9):
    def on_key_pressed(e):
        for pt in pts:
            dot.center = pt
            mtch_fig.canvas.draw()
            dot_ind = input("Input marker id: ")
            dot.set_label(dot_ind)
            unlabeled_proj[cam][dot_ind] = pt
            mtch_fig.canvas.draw()

    unlabeled_proj = {}
    unlabeled_proj[cam] = {}
    click_fig = plt.figure()
    plt.imshow(img)
    pts = plt.ginput(clicks, timeout=0, show_clicks=True, mouse_add=1, mouse_pop=3, mouse_stop=2)
    print("ginput finished")

    mtch_fig = plt.figure()
    ax = mtch_fig.add_subplot(111)
    ax.imshow(img)
    dot = ptch.Circle((0, 0), radius=radius, color="red", alpha=alpha)
    ax.add_artist(dot)
    mtch_fig.canvas.mpl_connect("key_press_event", on_key_pressed)
    plt.show()
    print(pts)

    return unlabeled_proj

