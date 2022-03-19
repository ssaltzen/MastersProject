from operator import truediv
import os
import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import heapq
import random
import collections


#Used for constructing the graph of windows
#Holds the start index, end index, distance, and kNN label for each window
class Node:
    def __init__(self, start_index, end_index, distance, label):
        self.start_index = start_index
        self.end_index = end_index
        self.distance = distance
        self.label = label
        self.child_nodes = []
        self.index = 0

    #Less than definition for use in the priority queue used in dijkstra
    def __lt__(self, other):
        if self.distance <= other.distance:
            return True
        else:
            return False
    #Less than or equal to definition
    def __le__(self, other):
        if self.distance <= other.distance:
            return True
        else:
             return False

    def add_child(self, node):
        self.child_nodes.append(node)

    def __str__(self):

        return 'Node(start = {start}, end = {end}, distance = {distance}, label = {label})'.format(
            start = self.start_index,
            end = self.end_index,
            distance = self.distance,
            label = self.label
        )

    def __repr__(self):
        return self.__str__()

#Shortest path search to find the best combination of windows
def dijkstra(start, end, Graph):
    dist = [1e9]* len(Graph)
    dist[start] = 0
    prev = [None] * len(Graph)
    path = []
    pq = [(0, Graph[start])]

    while len(pq) > 0:
        current_distance, v_node = heapq.heappop(pq)
        if current_distance > dist[v_node.index]:
            continue

        for node in v_node.child_nodes:
            distance = current_distance + node.distance
            if distance < dist[node.index]:
                dist[node.index] = distance
                prev[node.index] = v_node
                heapq.heappush(pq, (distance, node))
    u = Graph[end]
    if prev[u.index] is not None or end == start:
        while u is not None:
            path.insert(0, u)
            u = prev[u.index]
    
    return path


#label_csv_file is a csv file that has one column titled 'File' containing the csv files which contain the maneuvers and the next column titled 'Maneuver' contains the labels for each file
#labeled_files_directory is the path to the folder which contains the files in the 'File' column of label_csv_file
#file_to_predict is the path to the file that windowed_kNN is used to predict 
#window_size_list is the list of values used for the individual window sizes that are each compared to the labeled files to predict the label for each window
def windowed_kNN(label_csv_file, labeled_files_directory, file_to_predict, k, window_size_list):

    labeled_data = pd.read_csv(label_csv_file)
    labeled_df = pd.DataFrame(labeled_data)

    file_names = labeled_df['File'].to_numpy()
    labels = labeled_df['Maneuver'].to_numpy()

    data = pd.read_csv(file_to_predict)
    df = pd.DataFrame(data)

    #Get the four features of interest from the flight path file, head in the dataset is short for heading, which is the yaw (rotation around the z axis)
    arr_head = df[' head (deg)'].to_numpy()
    arr_pitch = df[' pitch (deg)'].to_numpy()
    arr_roll = df[' roll (deg)'].to_numpy()
    arr_vz = df[' vz (m/s)'].to_numpy()

    print(len(arr_head))

    dhead = []
    dpitch = []
    droll = []
    vz = []

    #get the delta for the rotation datapoints at each index, as this is the most useful for measuring the similarity between maneuvers
    #The absolute value of the difference in roll and heading is used, as rolling left and rolling right should be equivelant for identifying a maneuver.
    #The absolute value of the difference in pitch is not used, because pitching up and pitching down should have different significance for maneuvers
    for i in range(1, len(arr_head)):
        dhead.append(abs(arr_head[i] - arr_head[i-1]))
        dpitch.append(arr_pitch[i] - arr_pitch[i-1])
        droll.append(abs(arr_roll[i] - arr_roll[i-1]))
        vz.append(arr_vz[i])

    #array to store the kNN distance and label calculated for each window
    window_distances = []
    
    #Loop over the different window sizes
    for base_window_size in window_size_list:
        window_size = base_window_size
        
        #Array to store each window of the window size currently being used
        windows = []

        #Slide the window across the file, skipping 1 second (5 indices) each iteration to shorten the runtime
        for j in range(0, len(dhead) - window_size, 5):
            min_label = ''
            start_index = 0

            #Get the datapoints within the current window
            window_dhead = dhead[j:window_size + j]
            window_dpitch = dpitch[j:window_size + j]
            window_droll = droll[j:window_size + j]
            window_vz = vz[j:window_size + j]

            distancesWithLabels = []

            #Loop over training data, comparing each file to the current window using Dynamic Time Warping.
            for data_file, label in zip(file_names, labels):
                abs_file_path = labeled_files_directory + '\\' + data_file
                file_data = pd.read_csv(abs_file_path)
                file_df = pd.DataFrame(file_data)

                file_arr_head = file_df[' head (deg)'].to_numpy()
                file_arr_pitch = file_df[' pitch (deg)'].to_numpy()
                file_arr_roll = file_df[' roll (deg)'].to_numpy()
                file_arr_vz = file_df[' vz (m/s)'].to_numpy()

                file_dhead = []
                file_dpitch = []
                file_droll = []
                file_vz = []

                for i in range(1, len(file_arr_head)):
                    file_dhead.append(abs(file_arr_head[i] - file_arr_head[i-1]))
                    file_dpitch.append(file_arr_pitch[i] - file_arr_pitch[i-1])
                    file_droll.append(abs(file_arr_roll[i] - file_arr_roll[i-1]))
                    file_vz.append(file_arr_vz[i])

                head_distance = 0
                pitch_distance = 0
                roll_distance = 0
                vz_distance = 0


                head_distance, _ = fastdtw(window_dhead, file_dhead, dist=euclidean)
                pitch_distance, _ = fastdtw(window_dpitch, file_dpitch, dist=euclidean)
                roll_distance, _ = fastdtw(window_droll, file_droll, dist=euclidean)
                vz_distance, _ = fastdtw(window_vz, file_vz, dist=euclidean)


                #Add the DTW distance for each individual feature together to get the multivariate DTW distance
                sum_distances = head_distance + pitch_distance + roll_distance + vz_distance
                distancesWithLabels.append((sum_distances, label))

            #Find the k nearest neighbors and assign the label to the window accordingly. Then assign the distance to be the lowest distance that matches the label
            distancesWithLabels.sort(key=lambda a: a[0])
            kNearestNeighbors = distancesWithLabels[0:k]
            counter = collections.Counter(element[1] for element in kNearestNeighbors)

            most_common_nearest_neighbor = []
            highest_count = 0
            for count in counter:
                if counter[count] > highest_count:
                    highest_count = counter[count]
                    most_common_nearest_neighbor = [count]
                elif counter[count] == highest_count:
                    most_common_nearest_neighbor.append(count)

            min_label = random.choice(most_common_nearest_neighbor)
            min_distance = 0
            for tuple in kNearestNeighbors:
                if tuple[1] == min_label:
                    min_distance = tuple[0]
                    break

                
            start_index = j
            end_index = j + window_size

            #store the distance, label, and start and end index for each window.
            windows.append((min_distance, min_label, start_index, end_index))
        window_distances.append(windows)

    filler_window = []
    total_distance = 0
    total_length = 0

    #Calculate the average distance per index to construct filler windows which will enable certain windows to be a part of the shortest path that otherwise would not be possible
    for i in range(len(window_distances)):
        for j in range(len(window_distances[i])):
            filler_distance = window_distances[i][j][0]
            start_index = window_distances[i][j][2]
            end_index = window_distances[i][j][3]
            total_distance += filler_distance
            total_length += end_index - start_index
    avg_dist_per_index = total_distance/total_length

    #Construct the filler windows using the average distance per index with a multiplier to penalize the use of filler windows in the shortest path
    for i in range(0, len(dhead) - 5, 5):
        start_index = i
        end_index = i + 5
        dist_per_index = 3*avg_dist_per_index
        filler_window_distance = dist_per_index * 5
        label = 'filler'
        filler_window.append((filler_window_distance, label, start_index, end_index))
    window_distances.append(filler_window)

    #start node and end node of the graph, start node will have an edge to all windows at the beginning of the file and all windows at the end of the file will have an edge to the end node
    start_node = Node(0, 0, 0, 'start')
    end_node = Node(0, 0, 1000, 'end')
    nodes = []
    index_counter = 0
    nodes.append(start_node)
    nodes[0].index = index_counter
    index_counter +=1

    #add edges to the start and end node
    for i in range(len(window_distances)):
        for j in range(len(window_distances[i])):
            node = Node(window_distances[i][j][2], window_distances[i][j][3], window_distances[i][j][0], window_distances[i][j][1])
            if j == 0:
                nodes[0].add_child(node)
            if node.end_index >= len(dhead) - 5 :
                node.add_child(end_node)
            node.index = index_counter
            index_counter += 1
            nodes.append(node)

    #Construct the rest of the directed graph, Window A has an edge to Window B if the start index of Window B matches the end index of Window A
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i == j:
                continue

            if nodes[i].end_index == nodes[j].start_index:
                nodes[i].add_child(nodes[j])
    end_node.index = index_counter
    nodes.append(end_node)
    print(file + ':')

    #Perform a shortest path search, finding the path with the minimum distance between the start and end node
    #This path should contain the windows that most closely matched the files that they were labeled as
    classification_list = dijkstra(0, end_node.index, nodes)
    maneuver_list = []
    #Remove the start and end node from the path and return the list
    for node in classification_list:
        if node.label != 'start' and node.label != 'end':
            maneuver_list.append(node)
    return maneuver_list

allFiles = os.listdir("C:\\Users\\14172\\OneDrive\\Desktop\\Luke\'s Grad School Stuff\\271ML\\maneuvers_csv")
random.shuffle(allFiles)
this_dir = os.path.dirname(__file__)

labeled_maneuvers_file = 'C:\\Users\\14172\\OneDrive\\Desktop\\Luke\'s Grad School Stuff\\271ML\\4labeled.csv'
labeled_maneuvers_directory = 'C:\\Users\\14172\\OneDrive\\Desktop\\Luke\'s Grad School Stuff\\271ML\\labeled_maneuvers_csv'
base_window_sizes = [30, 40, 60, 80, 100, 120, 140, 200, 220]
counter = 0
for file in allFiles:
    rel_path = "maneuvers_csv/" + file
    abs_file_path = os.path.join(this_dir, rel_path)
    
    print(windowed_kNN(labeled_maneuvers_file, labeled_maneuvers_directory, abs_file_path, 3, base_window_sizes))
    
    counter += 1
    if counter == 100:
        break