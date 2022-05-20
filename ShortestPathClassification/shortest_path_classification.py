import os
import pandas as pd
from fastdtw import fastdtw
import heapq
import random
from itertools import repeat
from multiprocessing import Pool


#Folder containing the full dataset
DATASET_PATH = 'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\allTestData'

#csv file that maps each file in the training data to the correct label
TRAINING_DATA_LABELS = 'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\labeled_maneuvers_turns_separated.csv'

#folder containing all training data files
TRAINING_DATA_FILES = 'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\labeled_maneuvers_csv'


#Used for constructing the graph of sections of the flight path
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


#Pre-processing algorithm to get the sections of the flight path where the change in rotation of the aircraft is above a certain threshold, indicating a potential maneuver
def extract_maneuvers_from_file(fileName, numIndeces, time_threshold):
    maneuvers = []
    non_maneuvers = []

    file_path = DATASET_PATH + '\\' + fileName

    data = pd.read_table(file_path)
    df = pd.DataFrame(data)

    arr_head = df[' head (deg)'].to_numpy()
    arr_roll = df[' roll (deg)'].to_numpy()
    arr_pitch = df[' pitch (deg)'].to_numpy()
    arr_time = df['time (sec)'].to_numpy()

    dhead = []
    droll = []
    dpitch = []

    for i in range(len(arr_head)):
        dhead.append(abs(arr_head[i] - arr_head[i-1]))
        droll.append(abs(arr_roll[i] - arr_roll[i-1]))
        dpitch.append(abs(arr_pitch[i] - arr_pitch[i-1]))

    inManeuver = False
    inNonManeuver = True
    maneuverStart = 0
    maneuverEnd = 0
    nonManeuverStart = 0
    nonManeuverEnd = 0
    for i in range(len(dhead) - numIndeces):
        drollsum = 0
        dpitchsum = 0
        dheadsum = 0

        for j in range(numIndeces):
            drollsum += droll[i+j]
            dpitchsum += dpitch[i+j]
            dheadsum += dhead[i+j]

        sustained_droll = drollsum/numIndeces
        sustained_dpitch = dpitchsum/numIndeces
        sustained_dhead = dheadsum/numIndeces

        if sustained_droll > 0.40 or sustained_dpitch > 0.30 or sustained_dhead > 0.30:
            if inNonManeuver and i > 1:
                nonManeuverEnd = i-1
                non_maneuvers.append((nonManeuverStart, nonManeuverEnd))
                maneuverStart = i
                inManeuver = True
                inNonManeuver = False

        else:
            if inManeuver:
                maneuverEnd = i-1
                if arr_time[maneuverEnd] - arr_time[maneuverStart] > time_threshold:
                    maneuvers.append((maneuverStart + int(numIndeces/2), maneuverEnd + int(numIndeces/2)))
                nonManeuverStart = i
                inNonManeuver = True
                inManeuver = False

    if inManeuver and arr_time[len(dhead)-1] - arr_time[maneuverStart] > time_threshold:
        maneuvers.append((maneuverStart, len(dhead)-1))
    return maneuvers, non_maneuvers





#Shortest path search to find the best combination of comparisons to the labeled maneuvers
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


def calc_dtw_distance(labeled_files_directory, data_file, label, dhead, arr_pitch, arr_roll, vz):
    abs_file_path = labeled_files_directory + '\\' + data_file
    file_data = pd.read_csv(abs_file_path)
    file_df = pd.DataFrame(file_data)

    file_arr_head = file_df[' head (deg)'].to_numpy()
    file_arr_pitch = file_df[' pitch (deg)'].to_numpy()
    file_arr_roll = file_df[' roll (deg)'].to_numpy()
    file_vz = file_df[' vz (m/s)'].to_numpy()

    file_dhead = []
    for i in range(1, len(file_arr_head)):
        delta = file_arr_head[i] - file_arr_head[i-1]
        
        #Heading is measured in degrees so we need to check for a wrap-around between 0 and 360
        if delta > 300:
            file_dhead.append(-(360-file_arr_head[i] + file_arr_head[i-1]))
        elif delta < -300:
            file_dhead.append(360 - file_arr_head[i-1] + file_arr_head[i]) 
        else:
            file_dhead.append(file_arr_head[i] - file_arr_head[i-1])


    #List to store all comparisons between the labeled maneuver files and sections of the file being labeled
    comparisons = []

    #If the input file length is less than the training file length, we just perform one comparison between the two sequences
    if len(dhead) < len(file_dhead):
        head_distance, _ = fastdtw(dhead, file_dhead)
        pitch_distance, _ = fastdtw(arr_pitch, file_arr_pitch)
        roll_distance, _ = fastdtw(arr_roll, file_arr_roll)
        vz_distance, _ = fastdtw(vz, file_vz)

        sum_distances = head_distance + pitch_distance + roll_distance + vz_distance

        comparisons.append((sum_distances, label, 0, len(dhead) - 1))
    
    else:
        #For shorter training files, performing multiple calculations at each index with various sizes of input file sections is not neccessary
        if len(file_arr_head) < 45:
            for j in range(0, len(dhead) - len(file_dhead)):
                window_size = len(file_dhead)

                window_dhead = dhead[j:window_size + j]
                window_pitch = arr_pitch[j:window_size + j]
                window_roll = arr_roll[j:window_size + j]
                window_vz = vz[j:window_size + j]
                
                head_distance = 0
                pitch_distance = 0
                roll_distance = 0
                vz_distance = 0

                head_distance, _ = fastdtw(window_dhead, file_dhead)
                pitch_distance, _ = fastdtw(window_pitch, file_arr_pitch)
                roll_distance, _ = fastdtw(window_roll, file_arr_roll)
                vz_distance, _ = fastdtw(window_vz, file_vz)

                #Add the DTW distance for each individual feature together to get the multivariate DTW distance
                sum_distances = head_distance + pitch_distance + roll_distance + vz_distance
                comparisons.append((sum_distances, label, j, j + window_size))
        else:
            for j in range(5, len(dhead) - len(file_dhead) - 5, 5):
                window_size = len(file_dhead)

                #At each index in the input file, we want to compare sections of slightly different sizes to the training file
                #k is used to increase and decrease the size of the section
                for k in range(-4, 6):
                    window_dhead = dhead[j - k:window_size + j + k]
                    window_pitch = arr_pitch[j - k:window_size + j + k]
                    window_roll = arr_roll[j - k:window_size + j + k]
                    window_vz = vz[j - k:window_size + j + k]
                    
                    head_distance = 0
                    pitch_distance = 0
                    roll_distance = 0
                    vz_distance = 0

                    head_distance, _ = fastdtw(window_dhead, file_dhead)
                    pitch_distance, _ = fastdtw(window_pitch, file_arr_pitch)
                    roll_distance, _ = fastdtw(window_roll, file_arr_roll)
                    vz_distance, _ = fastdtw(window_vz, file_vz)

                    #Add the DTW distance for each individual feature together to get the multivariate DTW distance
                    sum_distances = head_distance + pitch_distance + roll_distance + vz_distance
                    comparisons.append((sum_distances, label, j - k, j + window_size + k))

    return comparisons






#label_csv_file is a csv file that has one column titled 'File' containing the csv files which contain the maneuvers and the next column titled 'Maneuver' contains the labels for each file
#labeled_files_directory is the path to the folder which contains the files in the 'File' column of label_csv_file
#df is the dataframe of the file that shortest_path_classification is used to predict 
#num_processes refers to the number of processes that will be used to calculate the dtw distance for each comparison
def shortest_path_classification(label_csv_file, labeled_files_directory, df, num_processes):

    labeled_data = pd.read_csv(label_csv_file)
    labeled_df = pd.DataFrame(labeled_data)

    file_names = labeled_df['File'].to_numpy()
    labels = labeled_df['Maneuver'].to_numpy()

    #Get the four features of interest from the flight path dataframe, head in the dataset is short for heading, which is the yaw (rotation around the z axis)
    arr_head = df[' head (deg)'].to_numpy()
    arr_pitch = df[' pitch (deg)'].to_numpy()
    arr_roll = df[' roll (deg)'].to_numpy()
    arr_vz = df[' vz (m/s)'].to_numpy()

    #get the change in heading at each index
    dhead = []
    for i in range(1, len(arr_head)):
        delta = arr_head[i] - arr_head[i-1]
        
        #Heading is measured in degrees so we need to check for a wrap-around between 0 and 360
        if delta > 300:
            dhead.append(-(360-arr_head[i] + arr_head[i-1]))
        elif delta < -300:
            dhead.append(360 - arr_head[i-1] + arr_head[i]) 
        else:
            dhead.append(arr_head[i] - arr_head[i-1])

    #list to store the comparison distance and label calculated for each section of the file
    #Each element of the list is it's own list that contains the comparison distances for one training file at each index of the input file
    labeled_maneuver_comparisons = [] 
    
    #Each labeled file needs to be compared to every possible section of the file being classified (e.g. if the labeled file is of length 100 and the file being classified is length 200,
    # the labeled file will be compared to the following sections of the file being classified: [0:100], [1:101], ..., [100:200])
    #This process can be done in parallel for each labeled file.
    with Pool(num_processes) as p:  
        labeled_maneuver_comparisons = p.starmap(calc_dtw_distance, zip(repeat(labeled_files_directory), file_names, labels, repeat(dhead), repeat(arr_pitch), repeat(arr_roll), repeat(arr_vz)))


    #start node and end node of the graph, start node will have an edge to all sections at the beginning of the file and all sections at the end of the file will have an edge to the end node
    start_node = Node(0, 0, 0, 'start')
    end_node = Node(0, 0, 10000, 'end')
    nodes = []
    index_counter = 0
    nodes.append(start_node)
    nodes[0].index = index_counter
    index_counter +=1

    #labeled_maneuver_comparisons = merge_lists(labeled_maneuver_comparisons)
    comparison_list = []
    for tuple_list in labeled_maneuver_comparisons:
        for tuple in tuple_list:
            comparison_list.append(tuple)

    #Sort all nodes to be added to the graph by their start index, allowing us to use binary search to find all nodes that should share an edge in the graph
    comparison_list.sort(key=lambda a: a[2])

    #add edges to the start and end node
    min_start = comparison_list[0][2]
    for i in range(len(comparison_list)):
        #Each element of comparison list is of the format (dtw_distance, label, start_index, end_index)
        node = Node(comparison_list[i][2], comparison_list[i][3], comparison_list[i][0], comparison_list[i][1])
        if node.start_index == min_start:
            nodes[0].add_child(node)
        if node.end_index >= len(dhead) - 5 :
            node.add_child(end_node)
        node.index = index_counter
        index_counter += 1
        nodes.append(node)

    #Construct the rest of the directed graph, Comparison A has an edge to Comparison B if the start index of Comparison B matches the end index of Comparison A
    #Loop through all comparisons and use binary search on the sorted list of comparisons to add edges to the graph
    for i in range(len(nodes)):
        goal_start_index = nodes[i].end_index
        low = 0
        high = len(nodes) - 1
        mid = 0

        while low <= high:
            mid = (high + low) // 2

            if nodes[mid].start_index < goal_start_index:
                low = mid + 1
            
            elif nodes[mid].start_index > goal_start_index:
                high = mid - 1

            else:
                nodes[i].add_child(nodes[mid])
                break

        left_flag = False
        counter = 1
        while not left_flag and mid - counter >= 0:
            if nodes[mid - counter].start_index == goal_start_index:
                nodes[i].add_child(nodes[mid - counter])
                counter += 1
            else:
                left_flag = True

        right_flag = False
        counter = 1
        while not right_flag and mid + counter < len(nodes):
            if nodes[mid + counter].start_index == goal_start_index:
                nodes[i].add_child(nodes[mid + counter])
                counter += 1
            else:
                right_flag = True
    end_node.index = index_counter
    nodes.append(end_node)

    #Perform a shortest path search, finding the path with the minimum distance between the start and end node
    classification_list = dijkstra(0, end_node.index, nodes)
    maneuver_list = []
    #Remove the start and end node from the path and return the list
    for node in classification_list:
        if node.label != 'start' and node.label != 'end':
            maneuver_list.append(node)
    return maneuver_list


if __name__ == "__main__":
    labeled_maneuvers_file = TRAINING_DATA_LABELS
    labeled_maneuvers_directory = TRAINING_DATA_FILES

    fileList = os.listdir(DATASET_PATH)
    random.shuffle(fileList)

    counter = 0
    for file in fileList:
        abs_file_path = DATASET_PATH + '\\' + file
        data = pd.read_table(abs_file_path)
        df = pd.DataFrame(data)

        arr_head = df[' head (deg)'].to_numpy()
        arr_roll = df[' roll (deg)'].to_numpy()
        arr_pitch = df[' pitch (deg)'].to_numpy()
        arr_time = df['time (sec)'].to_numpy()
        arr_ = df['Unnamed: 0'].to_numpy()
        arr_xEast = df[' xEast (m)'].to_numpy()
        arr_yNorth = df[' yNorth (m)'].to_numpy()
        arr_zUp = df[' zUp (m)'].to_numpy()
        arr_vx = df[' vx (m/s)'].to_numpy()
        arr_vy = df[' vy (m/s)'].to_numpy()
        arr_vz = df[' vz (m/s)'].to_numpy()

        labeled_file = []

        #this step will remove all sections of the file where the change in rotation of the aircraft falls below a threshold. This threshold is used to separate steady flight from potential maneuvers.
        #The function returns a list conatining tuples where each tuple contains the start and end index of periods where the values were above the threshold.
        #This cuts down on a significant amount of computation by excluding a majority of the file from the dtw comparisons.
        maneuvers, _ = extract_maneuvers_from_file(file, 12, 10)
        print(maneuvers)
        for maneuver in maneuvers:
            maneuverStartIndex = maneuver[0]
            maneuverEndIndex = maneuver[1]
            head =arr_head[maneuverStartIndex:maneuverEndIndex]
            roll =arr_roll[maneuverStartIndex:maneuverEndIndex]
            pitch =arr_pitch[maneuverStartIndex:maneuverEndIndex]
            time_d =arr_time[maneuverStartIndex:maneuverEndIndex]
            indexArr =arr_[maneuverStartIndex:maneuverEndIndex]
            xEast =arr_xEast[maneuverStartIndex:maneuverEndIndex]
            yNorth =arr_yNorth[maneuverStartIndex:maneuverEndIndex]
            zUp =arr_zUp[maneuverStartIndex:maneuverEndIndex]
            vx =arr_vx[maneuverStartIndex:maneuverEndIndex]
            vy =arr_vy[maneuverStartIndex:maneuverEndIndex]
            vz =arr_vz[maneuverStartIndex:maneuverEndIndex]

            forDf = {'': indexArr, 'time (sec)': time_d, ' xEast (m)': xEast, ' yNorth (m)': yNorth, ' zUp (m)': zUp, ' vx (m/s)': vx, ' vy (m/s)': vy, ' vz (m/s)': vz, ' head (deg)': head, ' pitch (deg)': pitch, ' roll (deg)': roll}
            dfForLabel = pd.DataFrame(forDf)

            maneuver_list = shortest_path_classification(labeled_maneuvers_file, labeled_maneuvers_directory, dfForLabel, 6)
            start_idx = -1
            end_idx = -1
            turn_flag_right = False
            turn_flag_left = False

            #Filtering the labels from shortest_path_classification
            for node in maneuver_list:

                #We don't care about the steady flight labels, so we leave them out of the end result
                if node.label == 'Steady Flight' or node.label == 'filler Steady Flight':
                    continue

                #To find the boundary between back-to-back turns, we use the direction of the turn (turn left is counterclockwise and right is clockwise)
                #Additionally, turns are broken down into turn components in the labeled maneuver data so subsequent turn components with the same direction
                #are merged into a single turn.
                if node.label == 'Enter Turn Left' or node.label == 'Mid Turn Left' or node.label == 'Exit Turn Left' or node.label == 'Turn Left':
                    if turn_flag_right:
                        turn_flag_right = False
                        if end_idx - start_idx > 31:
                            labeled_file.append(("start = " + str(start_idx), "end = " + str(end_idx), "label = Turn"))
                    if not turn_flag_left:
                        turn_flag_left = True
                        start_idx = maneuverStartIndex + node.start_index
                        end_idx = maneuverStartIndex + node.end_index
                    else:
                        end_idx = maneuverStartIndex + node.end_index
                elif node.label == 'Enter Turn Right' or node.label == 'Mid Turn Right' or node.label == 'Exit Turn Right' or node.label == 'Turn Right':
                    if turn_flag_left:
                        turn_flag_left = False
                        if end_idx - start_idx > 31:
                            labeled_file.append(("start = " + str(start_idx), "end = " + str(end_idx), "label = Turn"))
                    if not turn_flag_right:
                        turn_flag_right = True
                        start_idx = maneuverStartIndex + node.start_index
                        end_idx = maneuverStartIndex + node.end_index
                    else:
                        end_idx = maneuverStartIndex + node.end_index

                #If the label is not a turn component or steady flight we can just add it to the list of maneuvers.
                #But first we need to check if the previous maneuver was a turn component and if it was we need to add the full turn to the list.
                else:
                    if turn_flag_left or turn_flag_right:
                        turn_flag_left = False
                        turn_flag_right = False
                        if end_idx - start_idx > 31:
                            labeled_file.append(("start = " + str(start_idx), "end = " + str(end_idx), "label = Turn"))
                    labeled_file.append(("start = " + str(maneuverStartIndex + node.start_index), "end = " + str(maneuverStartIndex + node.end_index), "label = " + str(node.label)))
            if turn_flag_left or turn_flag_right:
                turn_flag_left = False
                turn_flag_right = False
                if end_idx - start_idx > 31:
                    labeled_file.append(("start = " + str(start_idx), "end = " + str(end_idx), "label = Turn"))
        print("Final Labeled File:")
        print(file)
        print(labeled_file)
        print("\n\n")


        counter += 1
        if counter == 250:
            break

