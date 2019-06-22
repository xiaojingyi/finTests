#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-19 17:59:48$
# Note: This source file is NOT a freeware
# Version: Instant.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-19 17:59:48$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from ClassOrder import *
from ClassCluster import *
from ClassDataSrc import *
from ClassMarket import *
from ClassLine import *
import numpy as np
import random
import itertools
import matplotlib.pyplot as plt

class Instance(object):
    def __init__(self, config=False):
        if config:
            self.config = config
        self.stop_lose = self.config["stop_lose"]
        self.stop_win = self.config["stop_win"]
        self.pool_len = self.config["item_len"]
        self.mkt = Market(self.pool_len, self.config["mkt_type"])
        self.vec_hst = []
        self.plt_v = []
        self.i = 0

    def deal(self, signar, one):
        price = one[5]
        date_info = one[0] + " " + one[1]
        if signar == 1:
            if self.order.dealOpen() and self.order.deal["direction"] == OP_SELL:
                info = self.order.close(date_info, price, STOP_T_CMD)
                if info['profit']> 0:
                    plt.axvline(self.i-1, hold=None,label="order", color="g", linestyle=":")
                elif info["profit"] <= 0:
                    plt.axvline(self.i-1, hold=None,label="order", color="r", linestyle=":")
            info = self.order.open(date_info, OP_UP, price, price-self.stop_lose, price+self.stop_win)
            if info:
                plt.axvline(self.i, hold=None,label="order", color="g", linestyle="-")
        elif signar == 2:
            if self.order.dealOpen() and self.order.deal["direction"] == OP_UP:
                info = self.order.close(date_info, price, STOP_T_CMD)
                if info['profit']> 0:
                    plt.axvline(self.i-1, hold=None,label="order", color="g", linestyle=":")
                elif info["profit"] <= 0:
                    plt.axvline(self.i-1, hold=None,label="order", color="r", linestyle=":")
            info = self.order.open(date_info, OP_SELL, price, price+self.stop_lose, price-self.stop_win)
            if info:
                plt.axvline(self.i, hold=None,label="order", color="r", linestyle="-")
        elif signar == 3:
            info = self.order.close(date_info, price, STOP_T_CMD)
            if info:
                if info['profit']> 0:
                    plt.axvline(self.i-1, hold=None,label="order", color="g", linestyle=":")
                elif info["profit"] <= 0:
                    plt.axvline(self.i-1, hold=None,label="order", color="r", linestyle=":")
        return
    
    def clusterVec(self, vec):
        res = []
        for i in range(len(vec)):
            tmp = self.clfs[i].predict([vec[i]])
            res.append(tmp[0])
            
        return res
    
    def dataHandler(self, src=False):
        if not src:
            src  = self.config["src"]
        config = {
            "src": src,
            "item_len": 60,
            "train_len": 200,
            "test_len": 50,
        }
        datas = DataMatrixGen(config)
        return datas
    
    def dataLoop(self, show_step = 7000, callback=False, src=False, start=0, end=1000):
        if not src:
            src  = self.config["src"]
        print "looping..."
        self.loop_data = self.dataHandler(src)
        self.i = self.loop_data.i = start
        last_one = False
        while(1):
            self.i += 1
            one = self.loop_data.getLine()
            if not one:
                break
                
            callback(one)
            last_one = one
            
            if show_step != 0  and self.i % show_step == 0:
                print self.i
            
            if self.i >= end:
                break
                
        print "len: ", self.i - start
        print "loop done"
        return last_one
    
    def plot(self, res_show = True):
        print "ploting..."
        datas = self.dataHandler()
        self.mkt.reInit()
        self.i = 0
        price = []
        while(1):
            self.i += 1
            one = datas.getLine()
            if not one:
                break
                
            price.append(one[5])
            self.mkt.add(one)
            vec = self.mkt.get(self.config["pool_clean"])
            if vec:
                self.plotV(vec)
            
            if self.i % 7000 == 0:
                if res_show:
                    print self.i
        print "vec len: ", len(self.plt_v[0])
        print "len: ", self.i
        plt.plot(price)
        for one in self.plt_v:
            m = np.array(one)
            m_t = m.transpose()
            plt.plot(m_t[0], m_t[1])
        plt.savefig("demo.png")
        plt.show()
        print "ploting done"
        
    def plotV(self, vec):
        if len(self.plt_v) <= 0:
            self.plt_v = emptyNList(3)
        plt.axvline(20,hold=None,label="chg", color="r", linestyle=":")
        self.plt_v[0].append([self.i, vec["walk"][6]])
        self.plt_v[1].append([self.i, vec["crr"][3]])
        self.plt_v[2].append([self.i, vec["vol"][5]])
        
    def check(self, res_show = True):
        print "checking..."
        datas = self.dataHandler()
        self.order = Order(self.config["lose_move"], self.stop_lose)
        self.mkt.reInit()
        self.i = 0
        price_ls = []
        while(1):
            self.i += 1
            one = datas.getLine()
            if not one:
                break
#            print one
            price = one[5]
            price_ls.append(price)
            date_info = one[0] + " " + one[1] 

            self.order.tick(one[6], one[7], price)
            
            self.mkt.add(one)
            vec = self.mkt.get(self.config["pool_clean"])
            if vec:
                self.plotV(vec)
                self.vec_hst.append(vec)
#                print len(self.vec_hst)
                sig = self.sig(vec)
                if sig > 0:
                    self.deal(sig, one)
            
            if self.i % 7000 == 0:
                if res_show:
                    print one[0], one[1], self.mkt.pool.len, len(self.mkt.pool.data)
                    print self.i
                    self.order.info()
                    print "-------------------------"
        print "vec len: ", len(self.vec_hst)
        print "len: ", self.i
        self.order.close(date_info, price, STOP_T_CMD)
        res = self.order.info()
        if res:
            mkCsvFileWin("test_deals_info.csv", res)
            
        # plot image
        plt.plot(price_ls)
        for one in self.plt_v:
            m = np.array(one)
            m_t = m.transpose()
            plt.plot(m_t[0], m_t[1])
        plt.savefig("demo.png")
        plt.show()
        print "checking done"
        
    def sig(self, one):
        sig = 3
        if one["price"][0] > 0:
            sig = 2
        else:
            sig = 1
        return sig
    
    def afterCheck(self):
        return
    
    def printLoop(self, data):
        print data
            
    def loopTest(self):
        src="data/XAUUSD60.csv"
        self.dataLoop(10000, self.printLoop, src, 300, 400)

class IDefaultPredict(object):
    def __init__(self, init_conf, x_item_len):
        self.m = np.zeros(tuple(init_conf))
        self.x_item_len = x_item_len
        self.ct = 0
#        print self.m.shape
        
    def info(self):
        print "x len: ", self.ct
        m = self.m
        xsize = self.x_item_len
        size = len(m)

        ks = self.genMatrixKeys(size, xsize)
        sum_all = sum_ct = ct_all = 0
        for i in range(len(ks)):
            one_k = tuple(ks[i])
            data = m[one_k]
#            print one_k, data
            sum = abs(data[0])
            up = data[1]
            sell = data[2]
            ct = data[3]
            up_ct = data[4]
            sell_ct = data[5]
            ct_all += 1
            sum_all += sum
            sum_ct += ct
            print data,
            print sum, one_k
        print "------------------------"
        print sum_all, sum_ct, ct_all
        return
    
    def genMatrixKeys(self, size, x_size):
        res = list(itertools.product(range(size), repeat=x_size))
        return res
    
    def add(self, indexes, num):
        self.ct += 1
        self.m[tuple(indexes)][0] += num
        self.m[tuple(indexes)][1] += 1
        if num > 0:
            self.m[tuple(indexes)][2] += num
            self.m[tuple(indexes)][3] += 1
        elif num < 0:
            self.m[tuple(indexes)][4] += num
            self.m[tuple(indexes)][5] += 1
        
    def predict(self, indexes, e=0):
        walk = abs(self.m[tuple(indexes)][0])
        ct = self.m[tuple(indexes)][1]
        if ct > 0 and walk / ct > e:
            return self.m[tuple(indexes)][0]
        else:
            return 0
    
class Vecs(object):
    def __init__(self, indexes, cluster_n):
        self.m = np.array(indexes)
        self.m_tr = self.m.transpose()
        self.clfs = []
        self.cluster_price = []
        self.cluster_per = []
        self.cluster_vol = []
        self.cluster_n = cluster_n
        
    def calc(self):
        line_res = self.getClusters(self.m_tr)
        return self.calcRes(line_res, self.m)
    
    def getClusters(self, lines):
        len_lines = len(lines)
        res = []
        for i in range(len_lines):
            clf = ClusterKMeans(self.cluster_n, "cluster.kmeans.cache.vecs_%d.npy" % i)
            self.clfs.append(clf)
            data = lines[i].reshape(len(lines[i]-1), 1)
            clf.training(data, True)
            info = clf.getAllInfo()
#            print info[0]
            res.append(info)
        return res
    
    def calcRes(self, data, pri_data):
        res = []
#        print pri_data
        for i in range(len(data)):
            res.append([])
            cluster = data[i][0]
            labels = data[i][1]
            for l in labels:
                res[i].append([l])
            if i == 0:
                self.cluster_price = cluster
            elif i == 1:
                self.cluster_per = cluster
            elif i == 2:
                self.cluster_vol = cluster
        res = np.array(res)
        res = res.transpose()[0]
        X = res[:].tolist()
        Y = res[:, 0].tolist()
        Y_1 = pri_data[:, 0].tolist()
        x_last = X[-1][:]
        y_first = Y_1[0]
        del X[-1]
        del Y[0]
        del Y_1[0]
#        print np.array(X)
#        print len(X)
#        print np.array(Y)
#        print len(Y)
#        print np.array(Y_1)
#        print len(Y_1)
#        print x_last, y_first
        
        return X, Y, Y_1, x_last, y_first
    
if __name__ == "__main__":
    conf = {
#            "src": "data/XAUUSD1-hst-new.csv",
            "src": "data/XAUUSD60.csv",
            "stop_lose": 1000,
            "stop_win": 2000,
            "item_len": 20000,
        }
    t = Instance(conf)
#    t.check()
    t.plot()
    print "Hello World";
