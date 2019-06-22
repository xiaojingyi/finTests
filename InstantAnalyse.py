#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-15 18:47:07$
# Note: This source file is NOT a freeware
# Version: InstantAnalyse.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-15 18:47:07$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from ClassPredict import *
from ClassDataSrc import *
from ClassPredict import *
from ClassOrder import *
from ClassMarket import *
from lib.Util import *

class Analyse(object):
    config = False
    debug = False
    d = False
    p = False
    order = False
    stop_lose = 1000
    stop_win = 2000
    
    def __init__(self, debug = True):
        self.debug = debug
        self.config = {
            "src": "data/XAUUSD60.csv",
            "cluster_n": 10,
            "p": Predict,
            "p_pool_size": 60,
            "stop_lose": 1000,
            "stop_win": 2000,
            "market_pool": 60,
        }
        print "start running..."
    
    def conf(self, config=False):
        if config:
            self.config = config
            self.stop_lose = self.config["stop_lose"]
            self.stop_win = self.config["stop_win"]
            
        self.p = self.config["p"](self.config["p_pool_size"], self.config["cluster_n"])
        self.order = Order(True, self.stop_lose)
        self.mkt = Market(self.config["market_pool"])
        
    def trainning(self):
        self.d = DataSrc(self.config["src"])
        self.mkt.reInit()
        vecs = []
        index_price = []
        while(1):
            one = self.d.getLine()
            if not one:
                break
            price = one[5]
            walk = one[3]
            vol = one[4]
            vec = self._mkVec(one)
            if vec:
                vecs.append(vec)
                self.p.trainingAdd(vec)
#                index_price.append([price, vec[0]*50000, vec[1]*0.1])
                index_price.append([vec[0], vec[1], vec[2]])

        y = self.p.training()
        self.d.done()
        print index_price
        np.save("index_price.npy", index_price[:])
        mkCsvFileWin("index_price.csv", index_price[:])
        return y, vecs
    
    def run(self):
        self.d = DataSrc(self.config["src"])
        self.mkt.reInit()
        i = 0
        y = []
        vecs = []
        while(1):
            i += 1
            one = self.d.getLine()
            if not one:
                break
            price = one[5]
            date_info = one[0] + " " + one[1] 

            self.order.tick(one[6], one[7], price)

            vec = self._mkVec(one)
            if vec:
                res, cat = self.p.predict(vec)
                y.append(cat)
                vecs.append(vec)
                sig = self._giveSig(res)
                self._deal(sig, one)

            if i % 50 == 0:
                self.order.info()
                print "-------------------------"

        self.order.close(date_info, price, STOP_T_CMD)
        res = self.order.info()
        self.d.done()
        if res:
            mkCsvFileWin("test_deals_info.csv", res)
        print "res done"
        return y, vecs
    
    def _mkVec(self, one):
        self.mkt.add(one)
        vec = self.mkt.get(True)
        if vec:
            vec_t = vec["price"]
            vec_t.extend(vec["walk"])
            vec_t.extend(vec["vol"])
            vec_t.extend(vec["per"])
            return vec_t
        return False
    
    def _giveSig(self, indexes): # should be rewrite
        sig = 0
        next_e = indexes[2]
        if abs(next_e) > 0:
            if next_e > 0:
                sig = 1
            elif next_e < 0:
                sig = 2
        return sig
    
    def _deal(self, signar, one):
        price = one[5]
        date_info = one[0] + " " + one[1]
        if signar == 1:
            if self.order.dealOpen() and self.order.deal["direction"] == OP_SELL:
                self.order.close(date_info, price, STOP_T_CMD)
            self.order.open(date_info, OP_UP, price, price-self.stop_lose, price+self.stop_win)
        elif signar == 2:
            if self.order.dealOpen() and self.order.deal["direction"] == OP_UP:
                self.order.close(date_info, price, STOP_T_CMD)
            self.order.open(date_info, OP_SELL, price, price+self.stop_lose, price-self.stop_win)
        elif signar == 3:
            self.order.close(date_info, price, STOP_T_CMD)
        return
        
class AnalyseMarket(Analyse):
    def _giveSig(self, indexes):
        sig = 0
        next_e = indexes[2]
#        print next_e
        if abs(next_e) > 0.3:
            if next_e > 0:
                sig = 1
            elif next_e < 0:
                sig = 2
#            else:
#                sig = 3
        return sig
    
    def _mkVec(self, one):
        self.mkt.add(one)
        vec = self.mkt.get(True)
        if vec:
            vec_t = []
            vec_t.extend([ vec["per"][1]*20000 ])
#            vec_t.extend([ 1 ])
            vec_t.extend([ vec["vol"][0]*0.001 ])
#            vec_t.extend([ 1 ])
            vec_t.extend([ vec["price"][0] ])
            vec_t.extend([ vec["price"][0]*100 ])
#            vec_t.extend(vec["price"])
#            vec_t.extend(vec["walk"])
#            vec_t.extend(vec["vol"])
#            vec_t.extend(vec["per"])
            return vec_t
        return False
    
if __name__ == "__main__":
    print "Hello World";
