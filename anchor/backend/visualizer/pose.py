import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from pathlib import Path
from typing import List, Any, Tuple
import os, random

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
    point1[0:3, 3] = np.array([0.9, 0, 0])

    point2 = np.eye(4)
    point2[0:3, 3] = np.array([1, 1, 1])

    point3 = np.eye(4)
    point3[0:3, 3] = np.array([1, 1, -1])

    point4 = np.eye(4)
    point4[0:3, 3] = np.array([1, -1, 1])

    point5 = np.eye(4)
    point5[0:3, 3] = np.array([1, -1, -1])

    point1 = np.matmul(point1, transform)
    point2 = np.matmul(point2, transform)
    point3 = np.matmul(point3, transform)
    point4 = np.matmul(point4, transform)
    point5 = np.matmul(point5, transform)

    if random.random() < 0.2:
        plot_pyramid([point1[0:3, 3], point5[0:3, 3], point3[0:3, 3], point2[0:3, 3], point4[0:3, 3]], color, axes)
    plot_pyramid([point1[0:3, 3], point1[0:3, 3], point1[0:3, 3], point1[0:3, 3], point1[0:3, 3]], color, axes)
    plot_pyramid([point2[0:3, 3], point2[0:3, 3], point2[0:3, 3], point2[0:3, 3], point2[0:3, 3]], color, axes)
    plot_pyramid([point3[0:3, 3], point3[0:3, 3], point3[0:3, 3], point3[0:3, 3], point3[0:3, 3]], color, axes)
    plot_pyramid([point4[0:3, 3], point4[0:3, 3], point4[0:3, 3], point4[0:3, 3], point4[0:3, 3]], color, axes)
    plot_pyramid([point5[0:3, 3], point5[0:3, 3], point5[0:3, 3], point5[0:3, 3], point5[0:3, 3]], color, axes)

"""
    For debug purposes, it is sometimes useful to visualize poses to be able to determine 
    issues with axis notation
"""
def visualize_pose_list(): 
    plt3d = plt.figure().add_subplot(projection='3d')
    num =0

    for transform_path in os.listdir("/tmp/repro"): 
        num += 1
        transform = np.loadtxt(f"/tmp/repro/{transform_path}")
        if "anchor" in transform_path:
            plot_tranform(transform, 'green', plt3d)
        else: 
            plot_tranform(transform, 'blue', plt3d)
        if num == 2000:
            break



    plt.savefig((Path(__file__).parent / "out.png").as_posix(), dpi=1000)


visualize_pose_list()