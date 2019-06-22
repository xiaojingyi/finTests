#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-14 13:41:16$
# Note: This source file is NOT a freeware
# Version: ClassCat.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-14 13:41:16$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from sklearn import cluster
import numpy as np

class Cluster(object):
    n = 8
    clf = False
    load_cache = True
    cache_file = "caches/cluster.cache.npy"
    def __init(self, n):
        self.n = n
        return
    
    def getCenters(self):
        return self._getKey()[0]
    
    def getAllInfo(self):
        if not self._isTrained():
            keys = np.load(self.cache_file)
            self._setKey(keys)
            if not self._isTrained():
                return False
            
        return self._getKey()
    
    def info(self):
        if not self._isTrained():
            keys = np.load(self.cache_file)
            self._setKey(keys)
            if not self._isTrained():
                return False
            
        return self.clf.labels_
    
    def training(self, X, order_asc = False):
        self._training(X, order_asc)
        keys = self._getKey()
        self._saveRes(keys)

    def predict(self, X):
        if not self._isTrained():
            keys = np.load(self.cache_file)
            self._setKey(keys)
            if not self._isTrained():
                return False
        
        return self.clf.predict(X)
        
    def printOut(self):
        print "done"
        return
    
    def _saveRes(self, arr):
        np.save(self.cache_file, arr)
        
    def _training(self, X):
        return

    def _getKey(self):
        return
    
    def _setKey(self, keys):
        return
    
    def _isTrained(self):
        return False
    
class ClusterKMeans(Cluster):
    def __init__(self, n=0, cache_f="cluster.kmeans.cache.npy"):
        if n:
            self.n = n
        if self.n < 500:
            self.clf = cluster.KMeans(n_clusters = self.n, n_jobs = -1, precompute_distances = True)
#            self.clf = cluster.KMeans(n_clusters = self.n, precompute_distances = True)
        else:
            self.clf = cluster.MiniBatchKMeans(n_clusters = self.n, init_size=self.n*2)
        self.cache_file = "caches/"+cache_f
        
    def printOut(self):
        print self.clf.cluster_centers_
        
    def _training(self, X, order_asc = False):
        self.clf.fit(X)
        if order_asc:
            keys = self._getKey()
            centers = keys[0]
            labels = keys[1]
            inertia = keys[2]
#            print centers
            len_centers = len(centers)
            sorted_centers = centers.copy()
            sorted_centers.shape=len_centers
            sorted_centers.sort()
#            print sorted_centers
            new_centers = {}
            j = 0
            for one in sorted_centers:
                new_centers[one] = j
                j += 1
#            print new_centers
#            print labels
            for i in range(len(labels)):
                labels[i] = new_centers[centers[labels[i]][0]]
#            print labels
            sorted_centers = np.array(sorted_centers).reshape(len_centers, 1)
#            print sorted_centers
            self._setKey([sorted_centers, labels, inertia])
    
    def _getKey(self):
        return [
            self.clf.cluster_centers_, 
            self.clf.labels_, 
            self.clf.inertia_,
        ]
    
    def _setKey(self, keys):
        self.clf.cluster_centers_ = keys[0]
        self.clf.labels_ = keys[1]
        self.clf.inertia_ = keys[2]
        
    def _isTrained(self):
        try:
            a = self.clf.cluster_centers_
            return True
        except:
            return False
        
if __name__ == "__main__":
    print "Hello World";
