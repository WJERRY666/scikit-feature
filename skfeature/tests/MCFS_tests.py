from nose.tools import *
import scipy.io
from skfeature.function.sparse_learning_based import MCFS
from skfeature.utility import construct_W
from skfeature.utility import unsupervised_evaluation
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
import numpy as np

def test_mcfs():
    # load data
    from functools import partial
    #mat = scipy.io.loadmat('./data/COIL20.mat')
    #from sklearn.datasets import load_iris
    #X = mat['X']    # data
    #X = X.astype(float)
    #y = mat['Y']    # label
    #y = y[:, 0]
    
    from sklearn.datasets import load_iris
    iris = load_iris()
    X = iris.data
    y = iris.target
    
    # construct affinity matrix
    kwargs = {"metric": "euclidean", "neighborMode": "knn", "weightMode": "heatKernel", "k": 5, 't': 1}
    W = construct_W.construct_W(X, **kwargs)

    num_fea = 100    # specify the number of selected features
    num_cluster = 5    # specify the number of clusters, it is usually set as the number of classes in the ground truth, we will limit it to run the tests quicker
    
    pipeline = []
    mcfs_partial = partial(MCFS.mcfs, W=W, n_clusters=num_cluster)
    pipeline.append(('select top k', SelectKBest(score_func=mcfs_partial, k=num_fea)))
    model = Pipeline(pipeline)
    
    # set y param to be 0 to demonstrate that this works in unsupervised sense.
    selected_features = model.fit_transform(X, y=np.zeros(X.shape[0]))
    
    # perform evaluation on clustering task
    num_cluster = 20    # number of clusters, it is usually set as the number of classes in the ground truth
    
    # perform kmeans clustering based on the selected features and repeats 20 times
    nmi_total = 0
    acc_total = 0
    for i in range(0, 20):
        nmi, acc = unsupervised_evaluation.evaluation(X_selected=selected_features, n_clusters=num_cluster, y=y)
        nmi_total += nmi
        acc_total += acc

    # output the average NMI and average ACC
    print(('NMI:', float(nmi_total)/20))
    print(('ACC:', float(acc_total)/20))
    
    assert_true(float(nmi_total)/20 > 0.5)
    assert_true(float(acc_total)/20 > 0.5)