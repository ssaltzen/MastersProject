# AI-r Force Manuevers 

This repository contains the work for the final project of ECS 271 and the basis for the Master's Capstone Project of Siena Saltzen and Lukas Mohelbrock. 
The project is based on the AIA Maneuver Identifcation Challenge where in an effort to enable AI coaching and automatic maneuver grading in pilot training, the Air Force seeks to automatically identify and label each maneuver flown in this dataset from a catalog of around 30 maneuvers. 
We have apporched a subset of this challange for our class project. More Details about our work and methods are avalible in the documentation section in the provided reports.


## General Info

This project is still under devlopment 

###1. The Data
    - The Data set comes from the 
		- Motivation | https://maneuver-id.mit.edu
		- Data | https://maneuver-id.mit.edu/data
		- Info | 2.89GB/6,661 files of .tsv files containing aircraft positional/orientation over various intervals

    - Due to the privcay and confidental nature of the data, we are not released to share the actual files. All files are store locally on the devloper computers.
	
### 2. Current State of the Project
    - The dataset has been clean and modified to remove bad files and inaccuracies
    - We have created several visulizations for testing and verification purposes
    - There are several clustering algorithms with different degree of success
	- There are additional methods currently in progress including and HMM classifier
	
### 3. Next Steps
    - Streamlining and fine tuning the current classifiers
	- Adapting the results of unsupervised learning to use as base for some self supervised appraoches
	- Picking the most successful mauneuvers to implement in a real time classifier


## The Code

###- DataManagment ~ Contains files used to clean, validate and manage the dataset
	- vistutorial.py ~ Graphs a file of maneuver data in a 3D plot for vislization
	- rename.py ~ Early attempt at consistant file sorting, randomness, and quality control without central hosting
	- getvaluesfrommaneuvers.py ~ Splits the files into singular "maneuvers" based on delinations of "steady flight"
	
### - Clustering ~ Classifers for unsupervised learning
	- dtw.py ~ Dynamic Time Warping Classifer
	
###- ManeuverVis ~ Unity Project that allows 3D manipulation and visualization of flight paths in files

###- Documentation ~ Collection of code documentation, project reports, and reported results

###- HMM ~ Hidden Markov Model ~ Still in progress


