from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import os
import pandas as pd


fileName = "immelstrumExample.csv"
this_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(this_dir, fileName)
data = pd.read_csv(abs_file_path)
df = pd.DataFrame(data)

arr_head = df[' head (deg)'].to_numpy()
arr_roll = df[' roll (deg)'].to_numpy()
arr_pitch = df[' pitch (deg)'].to_numpy()


dhead = []
droll = []
dpitch = []



for i in range(len(arr_head)):
    dhead.append(abs(arr_head[i] - arr_head[i-1]))
    droll.append(abs(arr_roll[i] - arr_roll[i-1]))
    dpitch.append(abs(arr_pitch[i] - arr_pitch[i-1]))


allFiles = os.listdir("C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\maneuvers_csv")
distances = []
counter = 0
for file in allFiles:
    rel_path = "maneuvers_csv/" + file
    abs_file_path = os.path.join(this_dir, rel_path)
    file_data = pd.read_csv(abs_file_path)
    file_df = pd.DataFrame(file_data)

    file_arr_head = file_df[' head (deg)'].to_numpy()
    file_arr_roll = file_df[' roll (deg)'].to_numpy()
    file_arr_pitch = file_df[' pitch (deg)'].to_numpy()

    file_dhead = []
    file_droll = []
    file_dpitch = []

    for i in range(len(file_arr_head)):
        file_dhead.append(abs(file_arr_head[i] - file_arr_head[i-1]))
        file_droll.append(abs(file_arr_roll[i] - file_arr_roll[i-1]))
        file_dpitch.append(abs(file_arr_pitch[i] - file_arr_pitch[i-1]))

    if len(file_dhead) - len(dhead) > 20:
        multiplier = 0

        min_distance = -1
        while(len(dhead) + multiplier*10 < len(file_dhead)):
            new_file_dhead = file_dhead[multiplier*10:len(dhead) + multiplier*10]
            new_file_droll = file_droll[multiplier*10:len(dhead) + multiplier*10]
            new_file_dpitch = file_dpitch[multiplier*10:len(dhead)+multiplier*10]

            head_distance, head_path = fastdtw(dhead, new_file_dhead, dist=euclidean)
            roll_distance, roll_path = fastdtw(droll, new_file_droll, dist=euclidean)
            pitch_distance, pitch_path = fastdtw(dpitch, new_file_dpitch, dist=euclidean)

            distances_sum = head_distance + roll_distance + pitch_distance
            if min_distance == -1:
                min_distance = distances_sum
            elif distances_sum < min_distance:
                min_distance = distances_sum

            multiplier += 1
        sum_distances = min_distance
    else:
        head_distance, head_path = fastdtw(dhead, file_dhead, dist=euclidean)
        roll_distance, roll_path = fastdtw(droll, file_droll, dist=euclidean)
        pitch_distance, pitch_path = fastdtw(dpitch, file_dpitch, dist=euclidean)

        sum_distances = head_distance + roll_distance + pitch_distance
    
    distances.append((file, sum_distances))
    counter += 1
    if counter%100 == 0:
        print(counter)

    if counter%1000 == 0:
        distances.sort(key=lambda a: a[1])
        print(distances[:100])

distances.sort(key=lambda a: a[1])
print(distances[:500])






