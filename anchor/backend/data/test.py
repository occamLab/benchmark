import pickle
import matplotlib.pyplot as plt
import numpy as np

THRESHOLD = 1

# for frame_idx in range(0, 124, 10):
frame_idx = 124
print(frame_idx)
fname_temp = "/home/powerhorse/Desktop/daniel_tmp/benchmark/anchor/backend/data/.cache/firebase_data/training_ua-1328ccb71aa9831789d2e776b63a04f0_ayush_nov30_4/ace/debug_visualizer/point_cloud/{frame_idx}.npy"
fname = fname_temp.format(frame_idx=frame_idx)
data = np.load(fname)

fig = plt.figure()
ax = plt.axes(projection="3d")

ax.view_init(elev=0, azim=-90)
mask = data[:, 3] < THRESHOLD
print(sum(mask))
ax.plot(data[mask, 0], data[mask, 1], data[mask, 2], "bo")
print(data.shape)
plt.show()
