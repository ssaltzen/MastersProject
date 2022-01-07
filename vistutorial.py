import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import math
from mpl_toolkits import mplot3d
from pyquaternion import Quaternion, quaternion


this_dir = os.path.dirname(__file__)
rel_path = "data/VanceAFB_tsv/20210428_2_Immelman.min.tsv"
abs_file_path = os.path.join(this_dir, rel_path)

data = pd.read_table(abs_file_path)
df = pd.DataFrame(data)

print(df.count())


ax = plt.axes(projection="3d")

arr_x = df['xEast (m)'].to_numpy()
arr_y = df['yNorth (m)'].to_numpy()
arr_z = df['zUp (m)'].to_numpy()
arr_t = df['time (sec)'].to_numpy()
arr_head = df['head (deg)'].to_numpy()
arr_roll = df['roll (deg)'].to_numpy()
arr_pitch = df['pitch (deg)'].to_numpy()

time_jump = [0, 0]

#Since there's a large time jump in each maneuver, find the time jump and get the index
for i in range(1, arr_t.size):
    dt = arr_t[i] - arr_t[i-1]
    if dt > time_jump[0]:
        time_jump[0] = dt
        time_jump[1] = i



arr_x = arr_x[time_jump[1]:]
arr_y = arr_y[time_jump[1]:]
arr_z = arr_z[time_jump[1]:]
arr_head = arr_head[time_jump[1]:]
arr_roll = arr_roll[time_jump[1]:]
arr_pitch = arr_pitch[time_jump[1]:]

left_wingtip_x = []
left_wingtip_y = []
left_wingtip_z = []

right_wingtip_x = []
right_wingtip_y = []
right_wingtip_z = []

for i in range(0, arr_x.size):
    left_wingtip_x.append(-25)
    left_wingtip_y.append(1)
    left_wingtip_z.append(1)
    right_wingtip_x.append(25)
    right_wingtip_y.append(1)
    right_wingtip_z.append(1)

def Rx(theta):
  return np.matrix([[ 1, 0           , 0           ],
                   [ 0, math.cos(theta),-math.sin(theta)],
                   [ 0, math.sin(theta), math.cos(theta)]])
  
def Ry(theta):
  return np.matrix([[ math.cos(theta), 0, math.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-math.sin(theta), 0, math.cos(theta)]])
  
def Rz(theta):
  return np.matrix([[ math.cos(theta), -math.sin(theta), 0 ],
                   [ math.sin(theta), math.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

quaternions = []

for pitch_x, head_z, roll_y in zip(arr_pitch, arr_head, arr_roll):
    rotation_x = Rx(math.radians(pitch_x))
    rotation_y = Ry(math.radians(roll_y))
    rotation_z = Rz(math.radians(head_z))
    rotation_matrix = rotation_z * rotation_y * rotation_x
    quaternions.append(Quaternion(matrix=rotation_matrix))

for x, y, z, i in zip(arr_x, arr_y, arr_z, range(0, arr_x.size)):
    rotated_left_wingtip = quaternions[i].rotate([left_wingtip_x[i], left_wingtip_y[i], left_wingtip_z[i]])
    rotated_right_wingtip = quaternions[i].rotate([right_wingtip_x[i], right_wingtip_y[i], right_wingtip_z[i]])

    left_wingtip_x[i] = rotated_left_wingtip[0] + arr_x[i]
    left_wingtip_y[i] = rotated_left_wingtip[1] + arr_y[i]
    left_wingtip_z[i] = rotated_left_wingtip[2] + arr_z[i]

    right_wingtip_x[i] = rotated_right_wingtip[0] + arr_x[i]
    right_wingtip_y[i] = rotated_right_wingtip[1] + arr_y[i]
    right_wingtip_z[i] = rotated_right_wingtip[2] + arr_z[i]
     


""" for x in arr_x:
    left_wingtip_x.append(x - 10)
    right_wingtip_x.append(x + 10)

for y, z in zip(arr_y, arr_z):
    left_wingtip_y.append(y)
    left_wingtip_z.append(z)
    right_wingtip_y.append(y)
    right_wingtip_z.append(z)

for angle, i in zip(arr_roll, range(0, arr_roll.size)):
    left_wingtip_x[i] = left_wingtip_x[i] - 10*math.cos(math.radians(angle))
    left_wingtip_z[i] = left_wingtip_z[i] - 10*math.sin(math.radians(angle))
    right_wingtip_x[i] = right_wingtip_x[i] + 10*math.cos(math.radians(angle))
    right_wingtip_z[i] = right_wingtip_z[i] + 10*math.cos(math.radians(angle))

for angle, i in zip(arr_head, range(0, arr_head.size)):
    left_wingtip_x[i] = left_wingtip_x[i] - 10*math.cos(math.radians(angle))
    left_wingtip_y[i] = left_wingtip_y[i] - 10*math.sin(math.radians(angle))
    right_wingtip_x[i] = right_wingtip_x[i] + 10*math.cos(math.radians(angle))
    right_wingtip_y[i] = right_wingtip_y[i] + 10*math.sin(math.radians(angle)) """



ax.plot3D(arr_x, arr_y, arr_z)
ax.plot3D(right_wingtip_x, right_wingtip_y, right_wingtip_z)
ax.plot3D(left_wingtip_x, left_wingtip_y, left_wingtip_z)




plt.show()