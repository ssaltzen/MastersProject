# AI-r Force Maneuvers 

This repository contains the work for the Master's Capstone Project of Siena Saltzen and Lucas Moehlebrock. 
The project is based on the AIA Maneuver Identification Challenge where in an effort to enable AI coaching and automatic maneuver grading in pilot training, the Air Force seeks to automatically identify and label each maneuver flown in this dataset from a catalog of around 30 maneuvers. 
We have approached a subset of this challenge for our Master's Capstone project. More Details about our work and methods are available in the documentation section in the provided reports.


## General Info

### 1. The Data
    *The Data set comes from the AI Accelerator Distribution
		* Motivation | https://maneuver-id.mit.edu
		
		* Data | https://maneuver-id.mit.edu/data
		
		* Info | 2.89GB/6,661 files of .tsv files containing aircraft positional/orientation over various intervals

    * Due to the privacy and confidential nature of the data, we are not permitted to publically share the dataset. 
		All files are store locally on the developer’s computers.
	
### 2. Current State of the Project
    * The dataset has been clean and modified to remove bad files and inaccuracies
    * We have created several visualizations for testing and verification purposes
    * We have developed the Shortest Path Classification algorithm, which has a 91.8% accuracy in predicting maneuver labels from the dataset
	


## The Code
	Our final solution to the Maneuver Identification Challenge is the Shortest Path Classification algorithm
	(/ShortestPathClassification/shortest_path_classification.py)
	Video examples of each type of maneuver in our training dataset can be found on [Google Drive]( https://drive.google.com/drive/folders/1dLIYun9XqU5sNJYZ6UG4pjUI8mgEux6k?usp=sharing)
	The ShortestPathClassification folder also contains the output log with the results of running the classifier on 256 random files. It also contains an
	Excel file containing the results of validating 50 of the files from the output log.
	The output for each file follows the format:
		[(a,m), (b,n),...] - (a,m) and (b,n) are the parts of the file left after pre-processing (i.e. regions with potential maneuvers)
		Final Labeled File:
		file_name
		[(start, end, maneuver label),...] - This is the list of predicted labels for the entire file
	To validate results with the visualizer, copy file_name and paste it in the Input Field on the bottom left corner of the visualizer and press enter.

#### - DataManagment ~ Contains files used to clean, validate and manage the dataset
	vistutorial.py ~ Graphs a file of maneuver data in a 3D plot for visualization
	rename.py ~ Early attempt at consistent file sorting, randomness, and quality control without central hosting
	getvaluesfrommaneuvers.py ~ Splits the files into singular "maneuvers" based on delineations of "steady flight"
	
#### - Clustering ~ Classifiers for unsupervised learning
	ticc_clustering.py was our attempt at clustering maneuvers.
	
#### - ManeuverVis ~ Unity Project that allows 3D manipulation and visualization of flight paths in files
	The full Unity project was too large to add to github, however the Unity Assets folder contains the scripts and scenes that were used for the visualizer.
	An executable version of the visualizer will be made available through google drive.

#### - Documentation ~ Collection of code documentation, project reports, and reported results

#### -  HMM ~ Hidden Markov Model ~ Still in progress


