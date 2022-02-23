import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import math
from mpl_toolkits import mplot3d
from pyquaternion import Quaternion, quaternion

time_threshold = 6

def get_values_from_file(fileName, startIndex, endIndex):
    rel_path = "allTestData/" + fileName
    this_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(this_dir, rel_path)
    data = pd.read_table(abs_file_path)
    df = pd.DataFrame(data)

    arr_head = df[' head (deg)'].to_numpy()
    arr_roll = df[' roll (deg)'].to_numpy()
    arr_pitch = df[' pitch (deg)'].to_numpy()
    dhead = []
    droll = []
    dpitch = []

    for i in range(startIndex + 1, endIndex + 1):
        dhead.append(abs(arr_head[i] - arr_head[i-1]))
        droll.append(abs(arr_roll[i] - arr_roll[i-1]))
        dpitch.append(abs(arr_pitch[i] - arr_pitch[i-1]))

    sumdroll = 0
    sumdpitch = 0
    sumdhead = 0
    mindroll = droll[0]
    mindpitch = dpitch[0]
    mindhead = dhead[0]
    maxdroll = droll[0]
    maxdpitch = dpitch[0]
    maxdhead = dhead[0]

    for i in range(len(dhead)):
        sumdroll += droll[i]
        sumdpitch += dpitch[i]
        sumdhead += dhead[i]

        if droll[i] > maxdroll:
            maxdroll = droll[i]

        if droll[i] < mindroll:
            mindroll = droll[i]

        if dpitch[i] > maxdpitch:
            maxdpitch = dpitch[i]

        if dpitch[i] < mindpitch:
            mindpitch = dpitch[i]

        if dhead[i] > maxdhead:
            maxdhead = dhead[i]

        if dhead[i] < mindhead:
            mindhead = dhead[i]

    Avgs = [sumdhead/len(dhead), sumdpitch/len(dhead), sumdroll/len(dhead)]
    Maxs = [maxdhead, maxdpitch, maxdroll]
    Mins = [mindhead, mindpitch, mindroll]

    return Avgs, Maxs, Mins    


def get_values_from_file_sustained(fileName, startIndex, endIndex, numIndeces):
    rel_path = "allTestData/" + fileName
    this_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(this_dir, rel_path)
    data = pd.read_table(abs_file_path)
    df = pd.DataFrame(data)

    arr_head = df[' head (deg)'].to_numpy()
    arr_roll = df[' roll (deg)'].to_numpy()
    arr_pitch = df[' pitch (deg)'].to_numpy()
    dhead = []
    droll = []
    dpitch = []

    for i in range(startIndex + 1, endIndex + 1):
        dhead.append(abs(arr_head[i] - arr_head[i-1]))
        droll.append(abs(arr_roll[i] - arr_roll[i-1]))
        dpitch.append(abs(arr_pitch[i] - arr_pitch[i-1]))

    sumdroll = 0
    sumdpitch = 0
    sumdhead = 0

    drollsum = 0
    dpitchsum = 0
    dheadsum = 0

    for i in range(numIndeces):
        drollsum += droll[i]
        dpitchsum += dpitch[i]
        dheadsum += dhead[i]

    mindroll = drollsum/numIndeces
    mindpitch = dpitchsum/numIndeces
    mindhead = dheadsum/numIndeces
    maxdroll = drollsum/numIndeces
    maxdpitch = dpitchsum/numIndeces
    maxdhead = dheadsum/numIndeces

    for i in range(len(dhead)-numIndeces):
        sumdroll += droll[i]
        sumdpitch += dpitch[i]
        sumdhead += dhead[i]

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

        if sustained_droll > maxdroll:
            maxdroll = sustained_droll

        if sustained_droll < mindroll:
            mindroll = sustained_droll

        if sustained_dpitch > maxdpitch:
            maxdpitch = sustained_dpitch

        if sustained_dpitch < mindpitch:
            mindpitch = sustained_dpitch

        if sustained_dhead > maxdhead:
            maxdhead = sustained_dhead

        if sustained_dhead < mindhead:
            mindhead = sustained_dhead

    Avgs = [sumdhead/len(dhead), sumdpitch/len(dhead), sumdroll/len(dhead)]
    Maxs = [maxdhead, maxdpitch, maxdroll]
    Mins = [mindhead, mindpitch, mindroll]

    return Avgs, Maxs, Mins

def extract_maneuvers_from_file(fileName, numIndeces):
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


def writeManeuverToFile(dataFrame, fileName):
    rel_path = "maneuvers_csv/" + fileName
    this_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(this_dir, rel_path)
    dataFrame.to_csv(abs_file_path, sep=',', index=False)

allFiles = os.listdir("C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\allTestData")
for dataFile in allFiles:
    maneuvers, non_maneuvers = extract_maneuvers_from_file(dataFile, 8)
    rel_path = "allTestData/" + dataFile
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
    counter = 0
    for maneuver in maneuvers:
        print(maneuver)
        maneuverStartIndex = maneuver[0]
        maneuverEndIndex = maneuver[1]
        head =arr_head[maneuverStartIndex:maneuverEndIndex]
        roll =arr_roll[maneuverStartIndex:maneuverEndIndex]
        pitch =arr_pitch[maneuverStartIndex:maneuverEndIndex]
        time =arr_time[maneuverStartIndex:maneuverEndIndex]
        indexArr =arr_[maneuverStartIndex:maneuverEndIndex]
        xEast =arr_xEast[maneuverStartIndex:maneuverEndIndex]
        yNorth =arr_yNorth[maneuverStartIndex:maneuverEndIndex]
        zUp =arr_zUp[maneuverStartIndex:maneuverEndIndex]
        vx =arr_vx[maneuverStartIndex:maneuverEndIndex]
        vy =arr_vy[maneuverStartIndex:maneuverEndIndex]
        vz =arr_vz[maneuverStartIndex:maneuverEndIndex]

        forDf = {'': indexArr, 'time (sec)': time, ' xEast (m)': xEast, ' yNorth (m)': yNorth, ' zUp (m)': zUp, ' vx (m/s)': vx, ' vy (m/s)': vy, ' vz (m/s)': vz, ' head (deg)': head, ' pitch (deg)': pitch, ' roll (deg)': roll}
        dfForFile = pd.DataFrame(forDf)
        newFileName = dataFile[:len(dataFile)-8] + "_" + str(counter) +".min.csv"

        writeManeuverToFile(dfForFile, newFileName)
        counter+=1


# Avgs, Maxs, Mins = get_values_from_file_sustained("TRAIN_13000812002.min.tsv", 2604, 2693, 12)
# print(Avgs)
# print(Maxs)
# print(Mins)


# print(" ")
# print("Non-Maneuvers:")
# print(non_maneuvers)

# Avgs, Maxs, Mins = get_values_from_file_sustained("TRAIN_12001447003.min.tsv", 3378, 3498, 20)
# print("Averages (Head, Pitch, Roll):")
# print(Avgs)
# print(" ")
# print("Max Values (averaged over 20 indeces):")
# print(Maxs)
# print(" ")
# print("Min Values (averaged over 20 indeces):")
# print(Mins)