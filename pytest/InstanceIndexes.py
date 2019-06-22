#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-19 14:19:33$
# Note: This source file is NOT a freeware
# Version: InstantIndexes.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-19 14:19:33$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from ClassMarket import *
from ClassDataSrc import *
from ClassCluster import *
import numpy as np
import hashlib
from lib.Util import *
from Instance import *
import itertools

class IndexesMaker(Instance):
    def __init__(self, config):
        self.config = {
            "src": "data/XAUUSD60.csv",
            "cluster_n": 3,
            "market_pool": 60,
            "test_src": "data/XAUUSD1.csv",
            "stop_lose": 1000,
            "stop_win": 2000,
        }
        if config:
            self.config = config
        super(IndexesMaker, self).__init__(self.config)
        
        hash_str = ""
        for k in self.config.keys():
            if k != "test_src" and k != "stop_lose" and k != "stop_win":
                hash_str += str(self.config[k]) + ":::"
            
        self.confkey = md5(hash_str)
        try:
            self.is_old = (self.confkey == str(np.load("caches/indexes_maker_conf.npy")))
        except:
            self.is_old = False
        self.mkt = Market(self.config["market_pool"])
        self.vecs = []
        self.clf = False # for predict
        self.clfs = [] # for X cluster
        self.cluster_price = {} # for Y price
        self.cluster_vol = {} 
        self.cluster_per = {} 
        print "start making..."
    
    def training(self):
        print "--------------- training ---------------"
        indexes = []
        if self.is_old:
            indexes = np.load("caches/indexes.npy")
        else:
            indexes = np.array(self.mkIndexes())
        
        indexes_tr = indexes.transpose()
        print indexes
        print "---------------"
#        print indexes_tr
#        print np.corrcoef(indexes_tr)
        line_res = self.getClusters(indexes_tr)
        x, y, y_1 = self.calcRes(line_res, indexes)
        self.resMatrix(x, y, y_1)
        
        print "--------------- traning end ---------------"
        return
    
    def genMatrixKeys(self, size, x_size):
        res = list(itertools.product(range(size), repeat=x_size))
        return res
    
    def matrixOut(self, m, xsize):
        size = len(m)

        ks = self.genMatrixKeys(size, xsize)
        sum_all = sum_ct = ct_all = 0
        for i in range(len(ks)):
            one_k = tuple(ks[i])
            data = m[one_k]
            sum = abs(data[0])
            up = data[1]
            sell = data[2]
            ct = data[3]
            up_ct = data[4]
            sell_ct = data[5]
            if ct > 0:
                if sum * 1.0 / ct > 0:
                    self.clf.add(one_k, data[0])
                    ct_all += 1
                    sum_all += sum
                    sum_ct += ct
                    k_info = [
                        round(self.cluster_price[one_k[0]], 2), 
                        round(self.cluster_per[one_k[1]], 2), 
                        round(self.cluster_vol[one_k[2]], 2)
                    ]
#                    print k_info
#                    print data
#                    print sum, one_k
#                    print "--------------------"
        print "------------------------"
        print sum_all, sum_ct, ct_all
        return
    
    def resMatrix(self, x, y, y_1):
        print "--------------- matrix ---------------"
        x_item_len = len(x[0])
        cluster_len = len(self.cluster_price)
        init_conf = []
        for i in range(x_item_len):
            init_conf.append(cluster_len)
        self.clf = IDefaultPredict(init_conf)
        
        init_conf.append(6) # {"sum":0, "up":0, "sell":0, "ct":0, "up_ct":0, "sell_ct":0 }
        res = np.zeros(tuple(init_conf))
        print res.shape
        ct_all = 0
        for i in range(len(x)):
            walk = y_1[i]
            one_k = x[i]
            data = res[tuple(one_k)]
            ct_all += 1
            data[0] += walk
            data[3] += 1
            if walk >= 0:
                data[1] += walk
                data[4] += 1
            else:
                data[2] += walk
                data[5] += 1
#        print res

        self.cluster_price = self.cluster_price.reshape(cluster_len)
        self.cluster_per = self.cluster_per.reshape(cluster_len)
        self.cluster_vol = self.cluster_vol.reshape(cluster_len)
        print self.cluster_price
        print self.cluster_per
        print self.cluster_vol
        self.matrixOut(res, x_item_len)
        
        print "--------------- matrix end ---------------"
        return 
    
    def calcRes(self, data, pri_data):
        res = []
#        print pri_data
        for i in range(len(data)):
            res.append([])
            cluster = data[i][0]
            labels = data[i][1]
            for l in labels:
#                res[i].append([clusters[l][0]])
                res[i].append([l])
            if i == 0:
                self.cluster_price = cluster
            elif i == 1:
                self.cluster_per = cluster
            elif i == 2:
                self.cluster_vol = cluster
#            print "------------------"
#            print res[i]
        res = np.array(res)
        res = res.transpose()[0]
        X = res[:].tolist()
        Y = res[:, 0].tolist()
        Y_1 = pri_data[:, 0].tolist()
        del X[-1]
        del Y[0]
        del Y_1[0]
        print np.array(X)
        print len(X)
        print np.array(Y)
        print len(Y)
        print np.array(Y_1)
        print len(Y_1)
        
#        print self.cluster_price
#        from sklearn.tree import DecisionTreeClassifier
        from sklearn.tree import DecisionTreeRegressor
#        self.clf = DecisionTreeClassifier() #
        self.clf = DecisionTreeRegressor()
        self.clf.fit(X, Y)
        print self.clf.score(X, Y)
#        print clf.feature_importances_   
        return X, Y, Y_1
        
    def getClusters(self, lines):
        len_lines = len(lines)
        res = []
        for i in range(len_lines):
            clf = ClusterKMeans(self.config["cluster_n"], "cluster.kmeans.cache.index_%d.npy" % i)
            self.clfs.append(clf)
            info = False
            if not self.is_old:
                data = lines[i].reshape(len(lines[i]-1), 1)
                clf.training(data, True)
#            data = lines[i].reshape(len(lines[i]-1), 1) # debug use
#            clf.training(data, True) # debug use
            info = clf.getAllInfo()
            res.append(info)
        return res
    
    def mkIndexes(self):
        src = DataSrc(self.config["src"])
        self.mkt.reInit()
        while(1):
            one = src.getLine()
            if not one:
                break
            vec = self.getVec(one)
            if vec:
                self.vecs.append(vec)
        src.done()
        np.save("caches/indexes.npy", self.vecs)
        np.save("caches/indexes_maker_conf.npy", self.confkey)
        return self.vecs
        
    def getVec(self, one):
        self.mkt.add(one)
        vec = self.mkt.get(True)
        if vec:
            vec_t = []
            vec_t.extend([ vec["price"][0] ])
            vec_t.extend([ vec["per"][0]*1000 ])
#            vec_t.extend([ 1 ])
#            vec_t.extend([ 1 ])
            vec_t.extend([ vec["vol"][0] ])
            return vec_t
        return False
    
if __name__ == "__main__":
    print "Hello World";
