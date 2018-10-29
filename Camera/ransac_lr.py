"""
"""

__author__ = "Liyan Chen"

import numpy as np
from sklearn import linear_model


def ransac_linear_regress(correspondence):
    x, y = [p[0] for p in correspondence], [p[1] for p in correspondence]
    ransac = linear_model.RANSACRegressor(residual_threshold=0.5)
    ransac.fit(np.reshape(x, (-1, 1)), y)
    return ransac.estimator_.coef_, ransac.estimator_.intercept_, len(ransac.inlier_mask_), sum(ransac.inlier_mask_)
