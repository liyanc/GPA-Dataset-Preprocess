"""
"""

__author__ = "Liyan Chen"

id2marker = ["ARIEL", "RBHD", "LBHD", "RFHD", "LFHD", "C7", "LBSH", "LFSH", "LUPA", "LELB", "LIEL", "LWRE", "LOWR",
             "LIWR", "LOHAND", "LIHAND", "CLAV", "T10", "STRN", "RFSH", "RBSH", "RUPA", "RELB", "RIEL", "RWRE", "RIWR",
             "ROWR", "RIHAND", "ROHAND", "LFWT", "LBWT", "RFWT", "RBWT", "LMWT", "RMWT", "LHIP", "LKNE", "LKNI", "LSHN",
             "LHEL", "LANK", "LMT5", "LMT1", "LTOE", "RHIP", "RKNE", "RKNI", "RSHN", "RHEL", "RANK", "RMT5", "RMT1",
             "RTOE"]
marker2id = {'ARIEL': 0, 'LMT1': 42, 'RKNI': 46, 'STRN': 18, 'LBHD': 2, 'ROWR': 26, 'LBWT': 30, 'RFHD': 3, 'RUPA': 21,
             'RANK': 49, 'LUPA': 8, 'LHIP': 35, 'RMT1': 51, 'RTOE': 52, 'LBSH': 6, 'LOWR': 12, 'RBHD': 1, 'LSHN': 38,
             'RSHN': 47, 'LKNI': 37, 'T10': 17, 'RHEL': 48, 'RMWT': 34, 'LFSH': 7, 'RIEL': 23, 'C7': 5, 'LKNE': 36,
             'RFWT': 31, 'ROHAND': 28, 'RBWT': 32, 'RHIP': 44, 'LOHAND': 14, 'RIWR': 25, 'RIHAND': 27, 'RELB': 22,
             'LTOE': 43, 'RBSH': 20, 'LANK': 40, 'LFHD': 4, 'LIEL': 10, 'LIWR': 13, 'LIHAND': 15, 'LELB': 9, 'RWRE': 24,
             'LFWT': 29, 'LMWT': 33, 'LWRE': 11, 'RFSH': 19, 'LMT5': 41, 'CLAV': 16, 'RMT5': 50, 'LHEL': 39, 'RKNE': 45}

assert dict((name, ind) for ind, name in enumerate(id2marker)) == marker2id, \
    "Inconsistent marker-id mapping. Data corrupted!"
