"""
"""

__author__ = "Liyan Chen"

import cv2
import numpy as np
import Camera as camsolve


def param2camproj(params):
    camproj = camsolve.CameraSolverNonlinear()
    camproj.load_params(params)
    return camproj


def aa_resize(img, scaling, interp=cv2.INTER_CUBIC, lp_filter=True):
    sigma_x, sigma_y = (1 / np.asarray(scaling, dtype=np.float32) - 1) / 2
    if sigma_x > 0 and sigma_y > 0 and lp_filter:
        imgarr = cv2.GaussianBlur(img, (0, 0), sigmaX=sigma_x, sigmaY=sigma_y)
    else:
        imgarr = img
    try:
        resized_img = cv2.resize(imgarr, None, fx=scaling[0], fy=scaling[1], interpolation=interp)
    except:
        print("ERROR:", img.shape, img.dtype, scaling)
    else:
        return resized_img
    return np.zeros([1080, 1080, 3], np.float32)


def valid_supp_pts(markers, joints):
    pts = np.concatenate([markers, joints], axis=0)
    # Keep only valid points
    vpts = pts[~np.any(np.isnan(pts), axis=1)]
    return vpts


def resize_pad_crop_img_with_camparams(
        img, world_p, params, target_dim=224, side_pad=8, addition_scaling_ratio=1.0,
        lp_filter=True, interp=cv2.INTER_CUBIC):
    # Load old camera parameters and project the 3D points
    camproj = param2camproj(params)
    imgpts = camproj.project_linear(world_p.T) if world_p.shape[0] > 0 else np.array([[1, 1]], np.float32)
    minx, maxx, miny, maxy = np.min(imgpts[:, 0]), np.max(imgpts[:, 0]), np.min(imgpts[:, 1]), np.max(imgpts[:, 1])

    # Decide scaling ratio based on skeleton sizes
    # Decide the axis to be centered along
    skel_size = max(maxx - minx, maxy - miny)
    is_x_longer = (maxx - minx > maxy - miny)
    max_scaling_ratio = float(target_dim - side_pad * 2) / skel_size if skel_size > 0 else 0.64
    scaling = min(addition_scaling_ratio * max_scaling_ratio, max_scaling_ratio)

    scaled_img = aa_resize(img, (scaling, scaling), interp, lp_filter)
    s_h, s_w, _ = scaled_img.shape

    # Bounding boxes on resized images
    sminx, smaxx, sminy, smaxy = np.array([minx, maxx, miny, maxy]) * scaling
    lenx, leny = smaxx - sminx, smaxy - sminy
    # Center the subject in the cropped area
    if is_x_longer:
        sminy -= (target_dim - side_pad - leny) / 2
    else:
        sminx -= (target_dim - side_pad - lenx) / 2

    # Decide paddings
    bminx, bminy = int(round(sminx - side_pad)), int(round(sminy - side_pad))
    top_pad = -min(bminx, 0)
    left_pad = -min(bminy, 0)
    bmaxx, bmaxy = bminx + target_dim, bminy + target_dim
    btn_pad = max(bmaxx - s_w, 0)
    right_pad = max(bmaxy - s_h, 0)

    # Calculate the new optical center
    # Move the bounding boxes according to paddings
    optical_center_offset = [bminx, bminy]
    bminx, bmaxx = bminx + top_pad, bmaxx + top_pad
    bminy, bmaxy = bminy + left_pad, bmaxy + left_pad

    # Pad the image
    r, c, chan = scaled_img.shape
    pre_r_pad = np.zeros((left_pad, c, chan), scaled_img.dtype)
    post_r_pad = np.zeros((right_pad, c, chan), scaled_img.dtype)
    pad_r_img = np.concatenate((pre_r_pad, scaled_img, post_r_pad))

    r, c, chan = pad_r_img.shape
    pre_c_pad = np.zeros((r, top_pad, chan), scaled_img.dtype)
    post_c_pad = np.zeros((r, btn_pad, chan), scaled_img.dtype)
    pad_c_img = np.concatenate((pre_c_pad, pad_r_img, post_c_pad), 1)

    # Scale the focal length according to the scaling factor
    # Offset the optical center accordingly
    e = np.copy(params[0])
    e[:2, :] *= scaling
    e[:2, 2] -= optical_center_offset
    new_params = (e, params[1], params[2], params[3], params[4])
    return pad_c_img[bminy:bmaxy, bminx:bmaxx, :], new_params
