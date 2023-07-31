import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from pathlib import Path
from typing import List, Any, Tuple
import os, random, re
from scipy.spatial.transform import Rotation as R


""" 
    Given 5 points, plots a pyramid into the current figure
    https://stackoverflow.com/questions/39408794/python-3d-pyramid
"""
def plot_pyramid(vertices: List[Tuple[float, float, float, float]], color: str, axes: plt.Axes):
    v = np.array([x for x in vertices])
    axes.scatter3D(v[:, 0], v[:, 1], v[:, 2])

    # generate list of sides' polygons of our pyramid
    verts = [ [v[0],v[1],v[4]], [v[0],v[3],v[4]],
    [v[2],v[1],v[4]], [v[2],v[3],v[4]], [v[0],v[1],v[2],v[3]]]

    # plot sides
    axes.add_collection3d(Poly3DCollection(verts, 
    facecolors=color, linewidths=1, edgecolors=color, alpha=.25))

"""
    Given a 4x4 transforms, plots a a pyramid visualizing it into the current figure
"""
def plot_tranform(transform: np.matrix, color: str, axes: plt.Axes):
    point1 = np.eye(4)
    point1[0:3, 3] = np.array([0.5, 0, 0])

    point2 = np.eye(4)
    point2[0:3, 3] = np.array([1, 1, 1])

    point3 = np.eye(4)
    point3[0:3, 3] = np.array([1, 1, -1])

    point4 = np.eye(4)
    point4[0:3, 3] = np.array([1, -1, 1])

    point5 = np.eye(4)
    point5[0:3, 3] = np.array([1, -1, -1])

    point1 = np.matmul(transform, point1)
    point2 = np.matmul(transform, point2)
    point3 = np.matmul(transform, point3)
    point4 = np.matmul(transform, point4)
    point5 = np.matmul(transform, point5)

    plot_pyramid([point1[0:3, 3], point5[0:3, 3], point3[0:3, 3], point2[0:3, 3], point4[0:3, 3]], color, axes)

"""
    For debug purposes, it is sometimes useful to visualize poses to be able to determine 
    issues with axis notation
"""
def visualize_pose_list(): 
    plt3d = plt.figure().add_subplot(projection='3d')
    plt3d.set_xlim(-3, 3)
    plt3d.set_ylim(-3, 3)
    plt3d.set_zlim(-3, 3)
    plt3d.set_xlabel("X")
    plt3d.set_ylabel("Y")
    plt3d.set_zlabel("Z")

    all_files = os.listdir("/tmp/repro")
    anchor_poses = [x for x in all_files if "anchor" in x]
    arkit_poses = [x for x in all_files if "arkit" in x]
    anchor_poses.sort(key=lambda x: re.findall('\d+', x))
    arkit_poses.sort(key=lambda x: re.findall('\d+', x))
    

    for idx, _ in enumerate(arkit_poses):
        arkit_pose = np.loadtxt(f"/tmp/repro/{arkit_poses[idx]}")
        anchor_pose = np.loadtxt(f"/tmp/repro/{anchor_poses[idx]}")

        plot_tranform(arkit_pose, 'blue', plt3d)
        plot_tranform(anchor_pose, 'green', plt3d)

        device_arkit_to_device_opencv = np.diag([1.0, -1.0, -1.0, 1.0])
        
        anchor_to_arkit = anchor_pose @ device_arkit_to_device_opencv @ np.linalg.inv(arkit_pose)
        plot_tranform(anchor_to_arkit, 'red', plt3d)

        print(anchor_to_arkit[0:3, 3])
        

    plt.savefig((Path(__file__).parent / "out.png").as_posix(), dpi=1000)


visualize_pose_list()