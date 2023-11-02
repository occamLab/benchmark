import json
import numpy as np
from pprint import pprint
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from pathlib import Path


def convert_to_4x4(raw_list_pose):
    return np.array(raw_list_pose).reshape(4, 4).transpose()


def compute_translation_error(translation_1, translation_2):
    return np.linalg.norm(translation_1 - translation_2)


def compute_rotational_error(rotation_1, rotation_2):
    angle_diff = np.linalg.inv(rotation_2) @ rotation_1
    trace = angle_diff[0, 0] + angle_diff[1, 1] + angle_diff[2, 2]
    return np.arccos((trace - 1) / 2)


def visualize_simd4x4(ace_4x4s, arkit_4x4s):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # ACE
    for ace_4x4 in ace_4x4s:
        translation = ace_4x4[:3, 3]
        ax.scatter(translation[0], translation[1], translation[2], c="r", marker="o")

    # ARKIT
    for arkit_4x4 in arkit_4x4s:
        translation = arkit_4x4[:3, 3]
        ax.scatter(translation[0], translation[1], translation[2], c="b", marker="x")

    plt.legend()

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    # Y is elevation, this shows X vs Z
    ax.view_init(elev=0, azim=90)
    plt.show()


def main():
    with open(
        Path(__file__).parent.parent
        / ".cache/iosLoggerDemo_processedJsons_test2_oct_19.json",
        "r",
    ) as rf:
        data = json.load(rf)["data"]

    print(convert_to_4x4(data[1]["ACE"]))
    aces = []
    arkits = []
    cas = []

    ace_translation_errors = []
    ace_rotational_errors = []
    ca_translation_errors = []
    ca_rotational_errors = []
    for frame in data:
        frame_num = frame["frame_num"]
        ace_4x4 = convert_to_4x4(frame["ACE"])
        aces.append(ace_4x4)
        arkit_4x4 = convert_to_4x4(frame["ARKIT"])
        arkits.append(arkit_4x4)
        ca_4x4 = convert_to_4x4(frame["CLOUD_ANCHOR"])
        cas.append(ca_4x4)

        ace_translation_error = compute_translation_error(
            ace_4x4[:3, 3], arkit_4x4[:3, 3]
        )
        ace_translation_errors.append(ace_translation_error)
        ace_rotational_error = compute_rotational_error(
            ace_4x4[:3, :3], arkit_4x4[:3, :3]
        )
        ace_rotational_errors.append(ace_rotational_error)

        ca_translation_error = compute_translation_error(
            ca_4x4[:3, 3], arkit_4x4[:3, 3]
        )
        ca_translation_errors.append(ca_translation_error)
        ca_rotational_error = compute_rotational_error(
            ca_4x4[:3, :3], arkit_4x4[:3, :3]
        )
        ca_rotational_errors.append(ca_rotational_error)
    print(
        f"ACE MEAN ERRORS {np.mean(ace_translation_errors)}, {np.mean(ace_rotational_errors)}"
    )
    print(
        f"CA MEAN ERRORS {np.mean(ca_translation_errors)}, {np.mean(ca_rotational_errors)}"
    )
    
    # visualize_simd4x4(aces, arkits)
    visualize_simd4x4(cas, arkits)


if __name__ == "__main__":
    main()
