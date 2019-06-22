#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-8 23:53:39$
# Note: This source file is NOT a freeware
# Version: Predict.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-8 23:53:39$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from sklearn import linear_model
from ClassMarket import *
import numpy as np
from ClassCluster import *
from ClassClusterTester import *

class Predict(object):
    pool = False
    cluster_n = 10
    vecs = []
    cache_file = "predict_vec.npy"
    predict_vec = []
    clf = False
    
    def __init__(self, psize=60, csize=10):
        self.pool = Pool(psize)
        self.cluster_n = csize
        self.vecs = []
        self.predict_vec = []
        
    def trainingAdd(self, one): # should be rewrite
        self.pool.add(one[0])
        if self.pool.reach_max:
            self.vecs.append(self.pool.getData())
            self.pool.clean()
    
    def training(self):
        self.clf = ClusterKMeans(self.cluster_n)
        self.clf.training(self.vecs)
        y = self.clf.info()
        self.clf.printOut()
        self.tester(y)
        return y
    
    def tester(self, y):
        tester = ClusterTester(self.cluster_n)
        tester.set(self.vecs, y, self.clf.getCenters())
        tester.printOut()
        self.predict_vec = tester.mkPredictVec()
        np.save(self.cache_file, self.predict_vec)
        print self.predict_vec
        
    def predict(self, one): # should be rewrite
        self.pool.add(one[0])
        if self.pool.reach_max:
            x = self.pool.getData()
            self.pool.clean()
            if len(self.predict_vec) <= 0:
                self.predict_vec = np.load(self.cache_file)
                if len(self.predict_vec) <= 0:
                    print "should training first!"
                    return [0,0,0], -1

            if not self.clf:
                self.clf = ClusterKMeans(self.cluster_n)
                
            p_cat = self.clf.predict(x)
            return self.predict_vec[p_cat[0]], p_cat[0]
            
        return [0,0,0], -1
    
class PredictMarket(Predict):
    def trainingAdd(self, one):
        self.vecs.append(one[:])
        
    def predict(self, one):
        x = one
        if len(self.predict_vec) <= 0:
            self.predict_vec = np.load(self.cache_file)
            if len(self.predict_vec) <= 0:
                print "should training first!"
                return [0,0,0], -1
            
        if not self.clf:
            self.clf = ClusterKMeans(self.cluster_n)
            
        p_cat = self.clf.predict(x)
        return self.predict_vec[p_cat[0]], p_cat[0]
    
    def tester(self, y):
        tester = ClusterTesterMarket(self.cluster_n)
        tester.set(self.vecs, y, self.clf.getCenters())
        tester.printOut()
        self.predict_vec = tester.mkPredictVec()
        np.save(self.cache_file, self.predict_vec)
        print self.predict_vec
        
if __name__ == "__main__":
    print "Hello World";
