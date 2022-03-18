import pandas as pd
import os
import sys
sys.path.insert(1,'C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\TICC')
from TICC_solver import TICC


if __name__ == '__main__':
    allFiles = os.listdir("C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\testFiles")
    filesTuples = []
    this_dir = os.path.dirname(__file__)
    for i in range(0,len(allFiles),2):
        filesTuples.append((allFiles[i], allFiles[i+1]))
    for tuple in filesTuples:
        rel_path = 'testFiles\\' + tuple[0]
        print(this_dir)
        abs_file_path = os.path.join(this_dir,rel_path)
        print(abs_file_path)
        fname = abs_file_path
        full_rel_path = 'testFiles\\' + tuple[1]
        full_abs_file_path = os.path.join(this_dir, full_rel_path)
        fullfname = full_abs_file_path
        print(fname)
        data = pd.read_csv(fname)
        df = pd.DataFrame(data)

        fulldata = pd.read_csv(fullfname)
        fulldf = pd.DataFrame(fulldata)
        fulldf.drop('Unnamed: 0',axis=1,inplace=True)


        bic_values = {}

        for i in range(3,15):
            ticc = TICC(window_size=5, number_of_clusters=i, lambda_parameter=90e-3, beta=400, maxIters=100, threshold=2e-5,
                            write_out_file=False, prefix_string="output_folder/", num_proc=1, compute_BIC=True, biased=True)
            (clustered_points, train_cluster_inverse, bic) = ticc.fit(input_file=fname)
            #clustered_points array doesn't start until the end of the first window, which will be index[window_size-1] of the original file. In order to add these values to the dataframe as their own column, we insert the cluster assignment of the first window at the beginning of the clustered_points array
            bic_values[i] = bic
            for _ in range(4):
                clustered_points = np.insert(clustered_points, 0, clustered_points[0])
            fulldf['cluster assignments'] = clustered_points
            
            
            fulldf.to_csv('C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\clustered\\' + tuple[0][:-4] +'_n_cluster_' + str(i) + '.csv')
            bic_df = pd.DataFrame([bic_values])
            for j, matrix in enumerate(train_cluster_inverse):
                clusters_df = pd.DataFrame(train_cluster_inverse[matrix])
                clusters_df.to_csv('C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\cluster_info\\' + tuple[0][:-4] +'_cluster' + str(j) + '_info_for_' + str(i) + '_clusters.csv')
            bic_df.to_csv('C:\\Users\\Luke\\Desktop\\Grad School\\Classes\\Masters Project\\visualization\\clustered\\' + tuple[0][:-4] +'_bic_values.csv')