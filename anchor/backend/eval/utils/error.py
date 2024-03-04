import numpy as np


def compute_translation_error(translation_1, translation_2):
    return np.linalg.norm(translation_1 - translation_2)


def compute_rotational_error(rotation_1, rotation_2):
    angle_diff = np.linalg.inv(rotation_2) @ rotation_1
    trace = angle_diff[0, 0] + angle_diff[1, 1] + angle_diff[2, 2]
    return np.arccos((trace - 1) / 2)
