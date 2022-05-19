import os
import pandas as pd
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import heapq
from itertools import repeat
from multiprocessing import Pool, Pipe, Manager
import multiprocessing
import time
import socket


OUTPUT_FILE_PATH = 'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\labeled_maneuvers_udp.csv'
TRAIN_DATA_LABELS = 'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\labeled_maneuvers_turns_separated.csv'
TRAIN_DATA_DIR = 'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\labeled_maneuvers_csv'


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



def extract_maneuvers_from_file(fileName, numIndeces, time_threshold):
    maneuvers = []
    non_maneuvers = []

    rel_path = "allTestData/" + fileName
    this_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(this_dir, rel_path)
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

        if sustained_droll > 0.45 or sustained_dpitch > 0.35 or sustained_dhead > 0.35:
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


def calc_dtw_distance(labeled_files_directory, data_file, label, dhead, arr_pitch, arr_roll, vz):
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
        file_dhead.append(file_arr_head[i] - file_arr_head[i-1])
        file_dpitch.append(file_arr_pitch[i] - file_arr_pitch[i-1])
        file_droll.append(file_arr_roll[i] - file_arr_roll[i-1])
        file_vz.append(file_arr_vz[i])

    #Array to store each window of the window size currently being used
    windows = []

    if len(dhead) < len(file_dhead):
        head_distance, _ = fastdtw(dhead, file_dhead)#, dist=euclidean)
        pitch_distance, _ = fastdtw(arr_pitch, file_arr_pitch)#, dist=euclidean)
        roll_distance, _ = fastdtw(arr_roll, file_arr_roll)#, dist=euclidean)
        vz_distance, _ = fastdtw(vz, file_vz)#, dist=euclidean)

        sum_distances = head_distance + pitch_distance + roll_distance + vz_distance

        windows.append((sum_distances, label, 0, len(dhead) - 1))
    
    else:
        for j in range(0, len(dhead) - len(file_dhead)):
            window_size = len(file_dhead)

            window_dhead = dhead[j:window_size + j]
            # window_dpitch = dpitch[j:window_size + j]
            # window_droll = droll[j:window_size + j]
            # window_vz = vz[j:window_size + j]

            
            # window_head = arr_head[j:window_size + j]
            window_pitch = arr_pitch[j:window_size + j]
            window_roll = arr_roll[j:window_size + j]
            window_vz = vz[j:window_size + j]
            
            head_distance = 0
            pitch_distance = 0
            roll_distance = 0
            vz_distance = 0

            head_distance, _ = fastdtw(window_dhead, file_dhead)#, dist=euclidean)
            # pitch_distance, _ = fastdtw(window_dpitch, file_dpitch, dist=euclidean)
            # roll_distance, _ = fastdtw(window_droll, file_droll, dist=euclidean)
            # vz_distance, _ = fastdtw(window_vz, file_vz, dist=euclidean)

            
            # head_distance, _ = fastdtw(window_head, file_arr_head, dist=euclidean)
            pitch_distance, _ = fastdtw(window_pitch, file_arr_pitch)#, dist=euclidean)
            roll_distance, _ = fastdtw(window_roll, file_arr_roll)#, dist=euclidean)
            vz_distance, _ = fastdtw(window_vz, file_vz)#, dist=euclidean)

            #Add the DTW distance for each individual feature together to get the multivariate DTW distance
            sum_distances = head_distance + pitch_distance + roll_distance + vz_distance
            windows.append((sum_distances, label, j, j + window_size))

    return windows

#label_csv_file is a csv file that has one column titled 'File' containing the csv files which contain the maneuvers and the next column titled 'Maneuver' contains the labels for each file
#labeled_files_directory is the path to the folder which contains the files in the 'File' column of label_csv_file
#file_to_predict is the path to the file that shortest_path_classification is used to predict 
#window_size_list is the list of values used for the individual window sizes that are each compared to the labeled files to predict the label for each window
def shortest_path_classification(label_csv_file, labeled_files_directory, df, num_processes):

    labeled_data = pd.read_csv(label_csv_file)
    labeled_df = pd.DataFrame(labeled_data)

    file_names = labeled_df['File'].to_numpy()
    labels = labeled_df['Maneuver'].to_numpy()

    # data = pd.read_csv(file_to_predict)
    # df = pd.DataFrame(data)

    #Get the four features of interest from the flight path file, head in the dataset is short for heading, which is the yaw (rotation around the z axis)
    classification_arr_head = df[' head (deg)'].to_numpy()
    classification_arr_pitch = df[' pitch (deg)'].to_numpy()
    classification_arr_roll = df[' roll (deg)'].to_numpy()
    classification_arr_vz = df[' vz (m/s)'].to_numpy()

    #print(len(arr_head))

    classification_dhead = []
    classification_dpitch = []
    classification_droll = []
    classification_vz = []

    #get the delta for the rotation datapoints at each index, as this is the most useful for measuring the similarity between maneuvers
    #The absolute value of the difference in roll and heading is used, as rolling left and rolling right should be equivelant for identifying a maneuver.
    #The absolute value of the difference in pitch is not used, because pitching up and pitching down should have different significance for maneuvers
    for i in range(1, len(classification_arr_head)):
        delta = classification_arr_head[i] - classification_arr_head[i-1]
        
        #Heading is measured in degrees so we need to check for a wrap-around between 0 and 360
        if delta > 300:
            classification_dhead.append(-(360-classification_arr_head[i] + classification_arr_head[i-1]))
        elif delta < -300:
            classification_dhead.append(360 - classification_arr_head[i-1] + classification_arr_head[i]) 
        else:
            classification_dhead.append(classification_arr_head[i] - classification_arr_head[i-1])

        classification_dpitch.append(classification_arr_pitch[i] - classification_arr_pitch[i-1])
        classification_droll.append(classification_arr_roll[i] - classification_arr_roll[i-1])
        classification_vz.append(classification_arr_vz[i])

    #array to store the kNN distance and label calculated for each window
    labeled_maneuver_comparisons = []
    
    #Loop over the different window sizes
    #for data_file, label in zip(file_names, labels):
    with Pool(num_processes) as p:  
        #windows = calc_dtw_distance(labeled_files_directory, data_file, label, dhead, arr_pitch, arr_roll)
        #window_distances.append(p.starmap(calc_dtw_distance, zip(repeat(labeled_files_directory), file_names, labels, repeat(dhead), repeat(arr_pitch), repeat(arr_roll), repeat(vz))))
        labeled_maneuver_comparisons = p.starmap(calc_dtw_distance, zip(repeat(labeled_files_directory), file_names, labels, repeat(classification_dhead), repeat(classification_arr_pitch), repeat(classification_arr_roll), repeat(classification_vz)))

    #start node and end node of the graph, start node will have an edge to all windows at the beginning of the file and all windows at the end of the file will have an edge to the end node
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

    comparison_list.sort(key=lambda a: a[2])
    #add edges to the start and end node
    min_start = comparison_list[0][2]
    for i in range(len(comparison_list)):
        node = Node(comparison_list[i][2], comparison_list[i][3], comparison_list[i][0], comparison_list[i][1])
        if node.start_index == min_start:
            nodes[0].add_child(node)
        if node.end_index >= len(classification_dhead) - 5 :
            node.add_child(end_node)
        node.index = index_counter
        index_counter += 1
        nodes.append(node)
    #Construct the rest of the directed graph, Window A has an edge to Window B if the start index of Window B matches the end index of Window A
    num_edges = 0
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
                num_edges += 1
                break

        left_flag = False
        counter = 1
        while not left_flag and mid - counter >= 0:
            if nodes[mid - counter].start_index == goal_start_index:
                nodes[i].add_child(nodes[mid - counter])
                num_edges += 1
                counter += 1
            else:
                left_flag = True

        right_flag = False
        counter = 1
        while not right_flag and mid + counter < len(nodes):
            if nodes[mid + counter].start_index == goal_start_index:
                nodes[i].add_child(nodes[mid + counter])
                num_edges += 1
                counter += 1
            else:
                right_flag = True
    end_node.index = index_counter
    nodes.append(end_node)

    #Perform a shortest path search, finding the path with the minimum distance between the start and end node
    #This path should contain the windows that most closely matched the files that they were labeled as
    classification_list = dijkstra(0, end_node.index, nodes)
    maneuver_list = []
    #Remove the start and end node from the path and return the list
    for node in classification_list:
        if node.label != 'start' and node.label != 'end':
            maneuver_list.append(node)
    return maneuver_list




BUFFER_LEN = 100 #in bytes

def initUDP(IP, port):
    #Create a datagram socket
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    #Enable immediate reuse of IP address
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    #Bind the socket to the port
    sock.bind((IP, port))
    #Set a timeout so the socket does not block indefinitely when trying to receive data
    sock.settimeout(0.5)

    return sock

def readUDP(sock):
    try:
        data, addr = sock.recvfrom(BUFFER_LEN)
    except socket.timeout as e:
        return b'Error'
    except Exception as e:
        return b'Error'
    else:
        return data

def check_udp(arr_head, arr_pitch, arr_roll, arr_vz, arr_time):
    # global arr_head
    # global arr_pitch
    # global arr_roll
    # global arr_vz
    # global arr_time
    sock = initUDP('127.0.0.1', 8888)
    time_flag = True
    time_start = 0
    time_end = 0
    while True:
        data = readUDP(sock)
        if data == b'Error':
            if time_flag:
                
                time_start = time.time()
                time_flag = False
            else:
                time_end = time.time()

            if time_end - time_start > 300:
                arr_time.append(-1)
                arr_vz.append(-1)
                arr_head.append(-1)
                arr_pitch.append(-1)
                arr_roll.append(-1)
                break
            continue
        else:
            time_flag = True
            info_string = data.decode('UTF-8')
            data_list = info_string.split(' ')
            vz = float(data_list[0])
            pitch = float(data_list[1])
            roll = float(data_list[2])
            head = float(data_list[3])
            _time = float(data_list[4])
            #[_time, vz, pitch, roll, head] = struct.unpack('fffff', data)
    
            
            arr_time.append(_time)
            arr_vz.append(vz)
            arr_head.append(head)
            arr_pitch.append(pitch)
            arr_roll.append(roll)

def label_data(maneuverStart, dfForLabel, arr_time):
    print("labeling\n\n")
    maneuver_list = shortest_path_classification(TRAIN_DATA_LABELS, TRAIN_DATA_DIR, dfForLabel, 6)
    saved_maneuvers = pd.read_csv(OUTPUT_FILE_PATH)
    start_idxs = saved_maneuvers['start'].to_numpy()
    end_idxs = saved_maneuvers['end'].to_numpy()
    maneuver_labels = saved_maneuvers['label'].to_numpy()
    start_idx = -1
    end_idx = -1
    turn_flag_right = False
    turn_flag_left = False
    labeled_file = []
    for node in maneuver_list:
        if node.label == 'Steady Flight' or node.label == 'filler' or node.label == 'filler Steady Flight':
            continue

        if node.label == 'Enter Turn Left' or node.label == 'Mid Turn Left' or node.label == 'Exit Turn Left' or node.label == 'Turn Left':
            if turn_flag_right:
                turn_flag_right = False
                if end_idx - start_idx > 30:
                    labeled_file.append(("start = " + str(arr_time[start_idx]), "end = " + str(arr_time[end_idx]), "label = Turn"))
            if not turn_flag_left:
                turn_flag_left = True
                start_idx = maneuverStart + node.start_index
                end_idx = maneuverStart + node.end_index
            else:
                end_idx = maneuverStart + node.end_index
        elif node.label == 'Enter Turn Right' or node.label == 'Mid Turn Right' or node.label == 'Exit Turn Right' or node.label == 'Turn Right':
            if turn_flag_left:
                turn_flag_left = False
                if end_idx - start_idx > 30:
                    labeled_file.append(("start = " + str(arr_time[start_idx]), "end = " + str(arr_time[end_idx]), "label = Turn"))
            if not turn_flag_right:
                turn_flag_right = True
                start_idx = maneuverStart + node.start_index
                end_idx = maneuverStart + node.end_index
            else:
                end_idx = maneuverStart + node.end_index
        else:
            if turn_flag_left or turn_flag_right:
                turn_flag_left = False
                turn_flag_right = False
                if end_idx - start_idx > 30:
                    labeled_file.append(("start = " + str(arr_time[start_idx]), "end = " + str(arr_time[end_idx]), "label = Turn"))
            labeled_file.append(("start = " + str(arr_time[maneuverStart + node.start_index]), "end = " + str(arr_time[maneuverStart + node.end_index]), "label = " + str(node.label)))
    if turn_flag_left or turn_flag_right:
        turn_flag_left = False
        turn_flag_right = False
        if end_idx - start_idx > 30:
            labeled_file.append(("start = " + str(arr_time[start_idx]), "end = " + str(arr_time[end_idx]), "label = Turn"))
    for labeled_maneuv in labeled_file:
        start_idxs = np.append(start_idxs, labeled_maneuv[0])
        end_idxs = np.append(end_idxs, labeled_maneuv[1])
        maneuver_labels = np.append(maneuver_labels, labeled_maneuv[2])
    forDF_file = {'start': start_idxs, 'end': end_idxs, 'label': maneuver_labels}
    dfForFile = pd.DataFrame(forDF_file)
    dfForFile.to_csv(OUTPUT_FILE_PATH, sep=',', index=False)
    print(labeled_file)
    print('\n\n')


def process_udp_data(arr_head, arr_pitch, arr_roll, arr_vz, arr_time):
    dhead = []
    dpitch = []
    droll = []
    last_index_checked = 0
    inManuever = False
    check_flag = True
    while True:
        if check_flag:
            inManeuver = False
            check_flag = False
        if arr_pitch._callmethod('__len__') > 9 and arr_pitch._callmethod('__len__') > last_index_checked:
            if arr_time[last_index_checked] == -1:
                if inManeuver:
                        maneuverEnd = last_index_checked-1
                        head =arr_head[maneuverStart:maneuverEnd]
                        roll =arr_roll[maneuverStart:maneuverEnd]
                        pitch =arr_pitch[maneuverStart:maneuverEnd]
                        time_d =arr_time[maneuverStart:maneuverEnd]
                        vz =arr_vz[maneuverStart:maneuverEnd]

                        forDf = {'time (sec)': time_d,' vz (m/s)': vz, ' head (deg)': head, ' pitch (deg)': pitch, ' roll (deg)': roll}
                        dfForLabel = pd.DataFrame(forDf)

                        
                        if arr_time[maneuverEnd] - arr_time[maneuverStart] > 6:
                            label_data(maneuverStart, dfForLabel, arr_time)
                            break
                break
            if(arr_time[last_index_checked] - arr_time[last_index_checked - 1] == 0):
                last_index_checked += 1
                continue
            dhead.append(abs(arr_head[last_index_checked] - arr_head[last_index_checked - 1])/(arr_time[last_index_checked] - arr_time[last_index_checked - 1]))
            dpitch.append(abs(arr_pitch[last_index_checked] - arr_pitch[last_index_checked - 1])/(arr_time[last_index_checked] - arr_time[last_index_checked - 1]))
            droll.append(abs(arr_roll[last_index_checked] - arr_roll[last_index_checked - 1])/(arr_time[last_index_checked] - arr_time[last_index_checked - 1]))
            
            sum_dhead = 0
            sum_dpitch = 0
            sum_droll = 0
            if last_index_checked >= 8:
                for i in range(last_index_checked - 8, last_index_checked + 1):
                    sum_dhead += dhead[i]
                    sum_dpitch += dpitch[i]
                    sum_droll += droll[i]

                avg_dhead = sum_dhead/8
                avg_dpitch = sum_dpitch/8
                avg_droll = sum_droll/8

                if avg_droll > 2.25 or avg_dpitch > 1.75 or avg_dhead > 1.75:
                    if not inManeuver:
                        maneuverStart = last_index_checked
                        inManeuver = True
                else:
                    if inManeuver:
                        maneuverEnd = last_index_checked-1
                        head =arr_head[maneuverStart:maneuverEnd]
                        roll =arr_roll[maneuverStart:maneuverEnd]
                        pitch =arr_pitch[maneuverStart:maneuverEnd]
                        time_d =arr_time[maneuverStart:maneuverEnd]
                        vz =arr_vz[maneuverStart:maneuverEnd]

                        forDf = {'time (sec)': time_d,' vz (m/s)': vz, ' head (deg)': head, ' pitch (deg)': pitch, ' roll (deg)': roll}
                        dfForLabel = pd.DataFrame(forDf)

                        
                        if arr_time[maneuverEnd] - arr_time[maneuverStart] > 6:
                            label_data(maneuverStart, dfForLabel, arr_time)

                        inManeuver = False
                
            last_index_checked += 1
        if last_index_checked == 1591:
            if inManeuver:
                        maneuverEnd = last_index_checked-1
                        head =arr_head[maneuverStart:maneuverEnd]
                        roll =arr_roll[maneuverStart:maneuverEnd]
                        pitch =arr_pitch[maneuverStart:maneuverEnd]
                        time_d =arr_time[maneuverStart:maneuverEnd]
                        vz =arr_vz[maneuverStart:maneuverEnd]

                        forDf = {'time (sec)': time_d,' vz (m/s)': vz, ' head (deg)': head, ' pitch (deg)': pitch, ' roll (deg)': roll}
                        dfForLabel = pd.DataFrame(forDf)

                        
                        if arr_time[maneuverEnd] - arr_time[maneuverStart] > 6:
                            label_data(maneuverStart, dfForLabel, arr_time)


if __name__ == "__main__":
    with Manager() as manager:
        arr_head = manager.list()
        arr_pitch = manager.list()
        arr_roll = manager.list()
        arr_vz = manager.list()
        arr_time = manager.list()
        p1 = multiprocessing.Process(target= check_udp, args = (arr_head, arr_pitch, arr_roll, arr_vz, arr_time))
        p2 = multiprocessing.Process(target= process_udp_data, args = (arr_head, arr_pitch, arr_roll, arr_vz, arr_time))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
