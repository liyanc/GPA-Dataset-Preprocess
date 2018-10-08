"""
"""

__author__ = "Liyan Chen"

from matplotlib import pyplot as plt
from matplotlib import patches as ptch


def get_marker_id(img, cam, unlabeled_dict, cam_proj, clicks=0, radius=6, alpha=0.9):
    def on_key_pressed(e):
        for pt in pts:
            dot.center = pt
            mtch_fig.canvas.draw()

            # Loop to get valid input
            while True:
                try:
                    dot_ind = int(input("Input marker id (-1 for invalid points): "))
                    if dot_ind in unlabeled_dict or dot_ind == -1:
                        break
                except ValueError:
                    pass

            dot.set_label(dot_ind)
            mtch_fig.canvas.draw()

            cam_proj[cam][dot_ind] = pt

        print("Labeling finished, press any key to redo. Close the windows otherwise.")

    # Show image for clicking
    cam_proj[cam] = {}
    click_fig = plt.figure()
    plt.imshow(img)
    pts = plt.ginput(clicks, timeout=0, show_clicks=True, mouse_add=1, mouse_pop=3, mouse_stop=2)
    print("close the old window now.")

    # Show image for matching
    mtch_fig = plt.figure()
    ax = mtch_fig.add_subplot(111)
    ax.imshow(img)
    dot = ptch.Circle((0, 0), radius=radius, color="red", alpha=alpha)
    ax.add_artist(dot)
    mtch_fig.canvas.mpl_connect("key_press_event", on_key_pressed)
    print("press any key to start matching")
    plt.show()

    return cam_proj

