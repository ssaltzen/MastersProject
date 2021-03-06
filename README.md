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
    *Integrated Data collection from the XPLane simulator through the SLPlugin


## The 	Classifier
	Our final solution to the Maneuver Identification Challenge is the Shortest Path Classification algorithm
	(/ShortestPathClassification/shortest_path_classification.py)
	Video examples of each type of maneuver in our training dataset can be viewed at https://drive.google.com/drive/folders/1dLIYun9XqU5sNJYZ6UG4pjUI8mgEux6k?usp=sharing
	The ShortestPathClassification folder also contains the output log with the results of running the classifier on 256 random files. It also contains an
	Excel file containing the results of validating 50 of the files from the output log.
	The output for each file follows the format:
		[(a,m), (b,n),...] - (a,m) and (b,n) are the parts of the file left after pre-processing (i.e. regions with potential maneuvers)
		Final Labeled File:
		file_name
		[(start, end, maneuver label),...] - This is the list of predicted labels for the entire file
	To validate results with the visualizer, copy file_name and paste it in the Input Field on the bottom left corner of the visualizer and press enter.
	
	/UDP/shortest_path_classification_udp.py contains the version of the classifier that works with the X-Plane plugin.

#### - DataManagment ~ Contains files used to clean, validate and manage the dataset
	vistutorial.py ~ Graphs a file of maneuver data in a 3D plot for visualization
	rename.py ~ Early attempt at consistent file sorting, randomness, and quality control without central hosting
	getvaluesfrommaneuvers.py ~ Splits the files into sections where the change in rotation is above a pre-determined threshold, removing regions of only steady flight which aren't of interest for classification.
	Cleaning The Data.py ~ Removes Duplicate Files, Missing Data Values, and Files that contain bad data
	
#### - Clustering ~ Classifiers for unsupervised learning
	ticc_clustering.py was our attempt at unsupervised learning using Toeplitz Inverse Covariance-Based Clustering.
	
#### - SLPlugin ~ Plugin that allows communciation between the XPlane Simulator and the classifier 
	SLPlugin.xpl ~ the complied DLL file - Drop into \X-Plane 11\Resources\plugins to run plugins 
	Additonal Files - Parts of the plugin project
	
#### - ManeuverVis ~ Unity Project that allows 3D manipulation and visualization of flight paths in files
	The full Unity project was too large to add to github, however the Unity Assets folder contains the scripts and scenes that were used for the visualizer.
	An executable version of the visualizer will be made available through google drive.

#### - Documentation ~ Collection of code documentation, project reports, and reported results
	ManeuverIdentification_FinalReport.pdf - Main Description of Full Project
	Project proposal Siena and Lucas.pdf - First Half of project, presented for ECS 271
	https://drive.google.com/file/d/1RprGphWdz4XWJOyqc4H0eQpzxaRHvl36/view?usp=sharing - Final Presentation 


