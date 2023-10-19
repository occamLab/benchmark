import json 
import numpy as np
from pprint import pprint 
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt

def convert_to_4x4(raw_list_pose):
    return np.array(raw_list_pose).reshape(4,4).transpose()

def compute_translation_error(translation_1, translation_2):
    return np.linalg.norm(translation_1 - translation_2)

def compute_rotational_error(rotation_1, rotation_2):
    
    angle_diff = np.linalg.inv(rotation_2) @ rotation_1
    trace = angle_diff[0,0] + angle_diff[1,1] + angle_diff[2,2]
    return np.arccos((trace-1)/2) 


def visualize_simd4x4(ace_4x4s, arkit_4x4s):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # ACE
    for ace_4x4 in ace_4x4s:
        translation = ace_4x4[:3, 3]
        ax.scatter(translation[0], translation[1], translation[2], c='r', marker='o')
        
    # ARKIT
    for arkit_4x4 in arkit_4x4s:
        translation = arkit_4x4[:3, 3]
        ax.scatter(translation[0], translation[1], translation[2], c='b', marker='x')

    plt.legend()

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Y is elevation, this shows X vs Z
    ax.view_init(elev=0, azim=90)
    plt.show()


def main():
    with open("cache/iosLoggerDemo_processedJsons_test2_oct_19.json", "r") as rf:
        data = json.load(rf)["data"]
    
    print(convert_to_4x4(data[1]["ACE"]))
    aces = []
    arkits = []
    
    translation_errors = []
    rotational_errors = []
    for frame in data:
        frame_num = frame["frame_num"]
        ace_4x4 = np.linalg.inv((convert_to_4x4(frame["ACE"]))) # INV TO FIX THEIR INVERSE
        aces.append(ace_4x4)
        arkit_4x4 = convert_to_4x4(frame["ARKIT"])
        arkits.append(arkit_4x4)
        
        # print(arkit_4x4[:3, :3])
        # print(ace_4x4)
        translation_error = compute_translation_error(ace_4x4[:3, 3], arkit_4x4[:3, :3])
        translation_errors.append(translation_error)
        rotational_error = compute_rotational_error(ace_4x4[:3, :3], arkit_4x4[:3, :3])
        rotational_errors.append(rotational_error)
        
        # print(f"at timestamp: {frame_num}, translation: {translation_error}, rotation: {rotational_error}")
   
    print(f"MEAN ERRORS {np.mean(translation_errors)}, {np.mean(rotational_errors)}")
    print(len(data))
    # visualize_simd4x4(aces, arkits)
        
        
        
        
        
if __name__ == "__main__":
    main()
