# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 11:49:51 2021

@author: Aneis Neztlas
"""

#\\13000016001.min.tsv

import os
import random 
random.seed(3)

ending = '.min.tsv'

allFiles = os.listdir()

def resetToDefault():
    allFilesReset = os.listdir()
    for fileName in allFilesReset:
        if fileName == 'rename.py':
            pass
        else:
            os.rename(fileName,fileName[6:])
       

#Uncomment this if running again with new names  
resetToDefault()     
  
    
       
for i in range(len(allFiles)):
    if allFiles[i] == 'rename.py':
       popPY = i
    else:
        allFiles[i] = allFiles[i][:-8]
        if not allFiles[i][0].isdigit():
            allFiles[i] = allFiles[i][6:]

allFiles.pop(popPY)

allFiles.sort(key=int)

print("Total Number of Files: ", len(allFiles))

testingTotal = len(allFiles)//3 #Testing will be 1/3 total

trainingValidTotal = (len(allFiles)//3)*2 #Training and Validation is 2/3

training = (trainingValidTotal//8)*7 #Training 3/4 T/V

validation = trainingValidTotal//8 #Validation is 1/4 T/V

#print(allFiles)

testingTotalList = []

trainingList = []

validationList = []


for i in range(testingTotal):
    index = random.randint(0, len(allFiles)-1)
    testingTotalList.append(allFiles[index])
    allFiles.pop(index)
    
for i in range(training):
    index = random.randint(0, len(allFiles)-1)
    trainingList.append(allFiles[index])
    allFiles.pop(index)

for i in range(validation):
    index = random.randint(0, len(allFiles)-1)
    validationList.append(allFiles[index])
    allFiles.pop(index)


print("Total # Testing: ", len(testingTotalList))
print("Total # Trainig: ", len(trainingList))   
print("Total # Valid: ", len(validationList))
print("Total # UnSorted: ", len(allFiles))

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))    

"""
print("testing and training")
print(intersection(testingTotalList, trainingList))

print("testing and valid")
print(intersection(testingTotalList, validationList))  

print("valid and training")
print(intersection(validationList, trainingList))  
"""

    
for fileName in testingTotalList:
   os.rename(fileName+ending,"TESTS_"+fileName+ending)

for fileName in validationList:
    if validationList.index(fileName)%2 == 0:
        os.rename(fileName+ending,"VAL_S_"+fileName+ending)
    else:
        os.rename(fileName+ending,"VAL_L_"+fileName+ending)

for fileName in trainingList:
    os.rename(fileName+ending,"TRAIN_"+fileName+ending)
