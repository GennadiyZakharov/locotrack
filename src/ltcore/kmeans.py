'''
Created on 06 Feb. 2015

@author: Gena
'''
from __future__ import division
from __future__ import print_function

from PyQt4 import QtCore

from pylab import plot,show


from scipy.cluster.vq import kmeans,vq


class KMeans(QtCore.QObject):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(KMeans, self).__init__(parent)
    
    
    
    def clusters(self, data, nClusters):
        # data generation
        
        #computing K-Means with K = 2 (2 clusters)
        centroids,_ = kmeans(data,nClusters)
        # assign each sample to a cluster
        idx,_ = vq(data,centroids)

        # some plotting using numpy's logical indexing
        plot(data[idx==0,0],data[idx==0,1],'ob',
             data[idx==1,0],data[idx==1,1],'or')
        plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
        show()
     