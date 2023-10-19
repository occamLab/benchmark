import numpy as np
import cv2
import math


"""
    This class is responsible to recieving ground truth and observed poses and outputting error statistics 
    The breakdowns in thresholds for error categories are based on the standard used in most papers
"""


class ErrorSummarizer:
    def __init__(self):
        self.total_observations = 0
        self.cm_1_degree_1 = 0  # 1 centimeter, 1 degree error
        self.cm_2_degree_2 = 0  # 2 centimeter, 2 degree error
        self.cm_5_degree_5 = 0  # 5 centimeter, 5 degree error
        self.cm_10_degree_5 = 0  # 10 centimeter, 5 degree error

        self.translation_errors = []
        self.rotation_errors = []

    def observe_pose(self, measured_pose: [float], ground_truth_pose: [float]):
        # print(ground_truth_pose)
        # print(measured_pose)

        measured_pose = np.reshape(measured_pose, (4, 4)).transpose()
        ground_truth_pose = np.reshape(ground_truth_pose, (4, 4)).transpose()

        error_matrix = np.matmul(np.linalg.inv(ground_truth_pose), measured_pose)
        error_rotation_matrix = error_matrix[0:3, 0:3]

        rotation_vector = cv2.Rodrigues(error_rotation_matrix)[0]
        rotation_error = np.linalg.norm(rotation_vector) * 180 / math.pi
        rotation_error = min(rotation_error, 180 - rotation_error)
        translation_error = float(
            np.linalg.norm(measured_pose[0:3, 3] - ground_truth_pose[0:3, 3])
        )
        translation_error *= 100
        assert rotation_error > 0 and rotation_error < 180
        assert translation_error > 0

        print(rotation_error, translation_error)

        if rotation_error < 1 and translation_error < 1:
            self.cm_1_degree_1 += 1
        if rotation_error < 2 and translation_error < 2:
            self.cm_2_degree_2 += 1
        if rotation_error < 5 and translation_error < 5:
            self.cm_5_degree_5 += 1
        if rotation_error < 5 and translation_error < 10:
            self.cm_10_degree_5 += 1

        self.total_observations += 1
        self.translation_errors += [translation_error]
        self.rotation_errors += [rotation_error]

    def print_statistics(self):
        self.translation_errors.sort()
        self.rotation_errors.sort()

        median_translation_error = self.translation_errors[
            len(self.translation_errors) // 2
        ]
        median_rotation_error = self.rotation_errors[len(self.rotation_errors) // 2]

        print("===================================================")
        print("Cloud Anchor Results.")
        print("Accuracy:")
        print(
            f"\t10cm/5deg: {(self.cm_10_degree_5 / self.total_observations) * 100:.1f}%"
        )
        print(
            f"\t5cm/5deg: {(self.cm_5_degree_5 / self.total_observations) * 100:.1f}%"
        )
        print(
            f"\t2cm/2deg: {(self.cm_2_degree_2 / self.total_observations) * 100:.1f}%"
        )
        print(
            f"\t1cm/1deg: {(self.cm_1_degree_1 / self.total_observations) * 100:.1f}%"
        )
        print(f"Median rotation error: {median_rotation_error} degrees")
        print(f"Median translation error: {median_translation_error} cm")
