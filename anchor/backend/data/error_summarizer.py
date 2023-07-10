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
        self.cm_1_degree_1 = 0      # 1 centimeter, 1 degree error
        self.cm_2_degree_2 = 0      # 2 centimeter, 2 degree error
        self.cm_5_degree_5 = 0      # 5 centimeter, 5 degree error
        self.cm_10_degree_5 = 0     # 10 centimeter, 5 degree error
        pass 
    
    def observe_pose(self, measured_pose: [float], ground_truth_pose: [float]):
        measured_pose = np.reshape(measured_pose, (4, 4)).transpose()
        ground_truth_pose = np.reshape(ground_truth_pose, (4, 4)).transpose()

        error_matrix = np.matmul(np.linalg.inv(ground_truth_pose), measured_pose)
        rotation_vector = cv2.Rodrigues(error_matrix)[0]
        rotation_error =  np.linalg.norm(rotation_vector) * 180 / math.pi
        translation_error = float(np.linalg.norm(measured_pose[0:3, 3] - ground_truth_pose[0:3, 3]))

        print("rotation error: ", rotation_error, " translation error: ", translation_error)

        pass

