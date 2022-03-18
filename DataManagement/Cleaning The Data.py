# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 20:18:00 2022

@author: Aneis Neztlas
"""


import os
import pandas as pd
import numpy as np
import hashlib


ending = '.min.tsv'

allFiles = os.listdir()
badFiles = []


#Check for mising Values
def removeInconsist():
    for fileName in allFiles:
        data = pd.read_csv(fileName, sep = "\t")
        df = pd.DataFrame(data)
        if np.any(df.isnull()):
            badFiles.append(fileName)
        if np.any(df.duplicated()):
            badFiles.append(fileName)
    return
            
        
#Remove Duplicate Files, removes second+ instance of a duplicate file
def removeDuplicates():
    unique = dict()
    for fileName in sorted(os.listdir('.'), reverse = True):
        if os.path.isfile(fileName):
            filehash = hashlib.md5(open(fileName, 'rb').read()).hexdigest()
    
            if filehash not in unique: 
                unique[filehash] = fileName
            else:
                badFiles.append(fileName)
                
    return           
                
                
                
removeInconsist()
removeDuplicates()
for file in badFiles:
    print(file)
    os.remove(file)