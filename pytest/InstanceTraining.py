#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-23 13:31:57$
# Note: This source file is NOT a freeware
# Version: InstanceTraining.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-23 13:31:57$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from ClassDataSrc import *
from ClassMarket import *
from Instance import *
import numpy as np
import itertools

class Training(Instance):
    def __init__(self, config=False):
#        self.config = {
#            "src": "data/XAUUSD60.csv",
#            "cluster_n": 3,
#            "item_len": 60,
#            "train_len": 200,
#            "test_len": 50,
#            "stop_lose": 1000,
#            "stop_win": 2000,
#        }
        if not config:
            print "no config in Training";
            exit()
        self.config = config
        super(Training, self).__init__(self.config)
        print "stop info:", -self.stop_lose, self.stop_win
        self.dmg = DataMatrixGen(self.config)
        self.res = []
        self.clf = False
        self.vec_pool = Pool(self.config["train_len"])
        self.indexes = []
        self.line = LineUnZero({
                "e_n": 3,
                "point_n": 10,
                "round": False,
            })
        self.last_walk = self.last_pwalk = self.last_price = 0
        
    def afterCheck(self):
        m = np.array(self.indexes, dtype=np.float64)
        np.save("caches/index.npy", m)
#        m = np.load("caches/index.npy")
        m = m.transpose()
        m[1] = abs(m[1])
#        m[0] = abs(m[0])
        print m
        
        walk = m[0][:].tolist()
        size_del = 1
        for i in range(size_del):
            del walk[-1]
        walk = np.array(walk, dtype=np.float64)
        print len (walk)
        
        price_p = m[1][:].tolist()
        for i in range(size_del):
            del price_p[0]
        price_p = np.array(price_p, dtype=np.float64)
        print len (price_p)
        
        per = m[2][:].tolist()
        for i in range(size_del):
            del per[-1]
        per = np.array(per, dtype=np.float64)
        
        m = np.corrcoef(np.array([walk, price_p, per]))
        print m
        
        from scipy import stats
        print stats.ttest_ind(walk,price_p)
        mkCsvFileWin("index_info.csv", self.indexes[:])
        
    def sig(self, vec):
        sig = 3
        walk = vec['walk'][0]
        price_walk = vec["price"][0]
        e = price_walk# * walk
        if e > 0:
            sig = 1
        elif e < 0:
            sig = 2
        return sig
        price = vec["crr"][3]
        if walk < 0 and self.last_walk > 0:
            price_walk = price - self.last_price# - vec["price"][0]
            self.last_price = price
            if price_walk > 0:
                sig = 2
            elif price_walk < 0:
                sig = 1
        self.last_walk = walk
        self.last_pwalk = vec["price"][0]
#        print sig
        return sig
        vec_info = self.vecInfo(vec)
        return 1
        self.vec_pool.add(vec_info)
        if self.vec_pool.reach_max:
#            print self.vec_pool.len
            v = Vecs(self.vec_pool.getData(), self.config["cluster_n"])
            x, y, y_, x_last, y_first = v.calc()
            
            x_item_len = len(x[0])
            cluster_len = self.config["cluster_n"]
            init_conf = []
            for i in range(x_item_len):
                init_conf.append(cluster_len)
            init_conf.append(6) # {"sum":0, "up":0, "sell":0, "ct":0, "up_ct":0, "sell_ct":0 }
            p = IDefaultPredict(init_conf, x_item_len) 
            
#            print len(x), len(y_)
            for i in range(len(x)):
                p.add(x[i], y_[i])
            p.info()
            
            e = p.predict(x_last, 0)
#        e = vec["walk"][0] * vec["price"][0]
    #            print e
            if e > 0:
                sig = 1
            elif e < 0:
                sig = 2
            else:
                sig = 3
    #            print x_last
        return sig
    
    def run(self):
        self.order = Order(True, self.stop_lose)
        while (True):
            print "start one ---------------------------------------"
#            data_m = self.dmg.getMs(self.config["item_len"] * self.config["train_len"])
            data_m = self.dmg.getMs(self.config["item_len"])
            if not data_m:
                break
            print "arrived: ", self.dmg.i
            print "data size: ", data_m["tr"].len
            m_tr = data_m["tr"]
#            print m_tr.m
#            print m_tr.len
            m_t = data_m["t"]
            x, y, y_, x_last, y_first = self.mkXY(m_tr)
            self.resMatrix(x, y, y_, x_last, y_first)
            self.order.info()
            print "end one ---------------------------------------"
#            break
        self.deal(3, ["last", "", 0, 0, 0, 0, 0])
        res = self.order.info()
        if res:
            mkCsvFileWin("tmp_deals_info.csv", res)
        self.matrixOut()
            
    def mkXY(self, m):
        self.mkt.reInit()
        length = m.len / self.config["item_len"]
        indexes = []
        for i in range(length):
            data = m.getChild(self.config["item_len"])
            indexes.append(self.getVec(data))
#        print indexes
        v = Vecs(indexes, self.config["cluster_n"])
        return v.calc()
    
    def resMatrix(self, x, y, y_1, x_last, y_first):
        print "--------------- matrix ---------------"
#        print x, y, y_1, x_last, y_first
        x_item_len = len(x[0])
        self.x_item_len = x_item_len
        self.res = []
        len_res = len(self.res)
        if len_res == 0:
            cluster_len = self.config["cluster_n"]
            init_conf = []
            for i in range(x_item_len*2):
                init_conf.append(cluster_len)
            self.clf = IDefaultPredict(init_conf)
            init_conf.append(6) # {"sum":0, "up":0, "sell":0, "ct":0, "up_ct":0, "sell_ct":0 }
            self.res = np.zeros(tuple(init_conf))
            print "shape:", self.res.shape
        ct_all = 0
        for i in range(len(x)):
            if i == 0:
                continue
            walk = y_1[i]
            one_k = x[i]
            one_k_prev = x[i-1]
            prev = self.res[tuple(one_k_prev)]
            data = prev[tuple(one_k)]
            ct_all += 1
            data[0] += walk
#            data[0] = walk
            data[3] += 1
            if walk >= 0:
#                data[1] = walk
                data[1] += walk
                data[4] += 1
            else:
                data[2] += walk
#                data[2] = walk
                data[5] += 1
        print "x_all: ", ct_all
        print self.res
        return
    
        #predict test
#        test_m = self.dmg.split(self.dmg.i+self.config["item_len"]*(self.config["train_len"]-1), self.config["item_len"])
#        lines = test_m.getChild()
#        test_walk = lines[self.config["item_len"]-1][5] - lines[0][9]
#        print test_m.m
#        print test_m.len
        print "next walk: ", test_walk
        
        print  "crr: ", x_last, self.res[tuple(x_last)]
#        if self.res[tuple(x_last)][3] != 0 and self.res[tuple(x_last)][0] / self.res[tuple(x_last)][3] > 0.5: 
#        if True:
        if x_last[0] != 1:
            sig = self.res[tuple(x_last)][0]
            print "sig: ", sig
            if sig > 0:
                self.deal(1, [str(self.dmg.i), "", 0, 0, 0, 100])
            elif sig < 0:
                self.deal(2, [str(self.dmg.i), "", 0, 0, 0, 100])
            else:
                self.deal(3, [str(self.dmg.i), "", 0, 0, 0, 100])
#        print self.res
        self.deal(3, [str(self.dmg.i), "", 0, 0, 0, 100+test_walk])
#        self.matrixOut()
        
        print "--------------- matrix end ---------------"
        return 
    
    def genMatrixKeys(self, size, x_size):
        res = list(itertools.product(range(size), repeat=x_size))
        return res
    
    def matrixOut(self):
        m = self.res
        xsize = self.x_item_len
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
                    print data,
                    print sum, one_k
#                    print "--------------------"
        print "------------------------"
        print sum_all, sum_ct, ct_all
        return
    
    def getVec(self, data):
        vec = self.mkt.calcSet(data)
        return self.vecInfo(vec)
    
    def vecInfo(self, vec):
        vec_t = []
        vec_t.extend([ vec["price"][0] ])
#        vec_t.extend([ vec["per"][0]*1000 ])
        vec_t.extend([ vec["walk"][6] ])
        vec_t.extend([ vec["vol"][5] ])
#        vec_t.extend([ vec["vol"][0] ])
        return vec_t
    
    def plotV(self, vec):
        if len(self.plt_v) <= 0:
            self.prev_walk_diff = 0
            self.prev_walk = 0
            self.plot_i = 0
            plt.axhline(1000, hold=None,label="chg", color="b", linestyle="-")
            self.plt_v = emptyNList(2)
#        walk = vec['walk'][1] * 3000.0/vec['walk'][6]
        walk = vec['walk'][6]*6*3
#        if walk > vec["crr"][3]:
#            walk = vec["crr"][3]
        walk_up_per = vec['walk'][1] * 2000.0/vec['walk'][6]
#        walk = -vec['per'][2]*1000
#        info = self.line.add(walk)
#        hl = info[5] * 150
#        print info[6], info[7]
#        price = vec["crr"][3] 
#        if hl > price:
#            hl = price
#        if vec["walk"][0] < 0 and self.prev_walk > 0:
#            plt.axvline(self.plot_i, hold=None,label="chg", color="r", linestyle=":")
        
        self.plt_v[0].append([self.i, walk])
        self.plt_v[1].append([self.i, walk_up_per])

        self.plot_i = self.i
        self.prev_walk = vec["walk"][0]
        
if __name__ == "__main__":
    config = {
            "src": "data/XAUUSD60.csv",
            "cluster_n": 3,
            "item_len": 60,
            "train_len": 200,
            "test_len": 50,
            "stop_lose": 1000,
            "stop_win": 2000,
        }
    t = Training(config)
#    t.run()
    t.check()
    print "Hello World";
