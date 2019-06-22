#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-14 17:02:34$
# Note: This source file is NOT a freeware
# Version: ClassClusterTester.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-14 17:02:34$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

class ClusterTester(object):
    res = {}
    n = 0
    def __init__(self, n):
        self.n = n
        for i in range(n):
            self.res[i] = {"sum": 0, "ct": 0, "up": 0, "sell": 0, "up_sum": 0, "sell_sum": 0}
    
    def set(self, X, Y, centers):
        len_data = len(Y)
        print "vecs number: ", len_data
        total_ct = 0
        for i in range(len_data):
            # next info
            if not self.res[Y[i]].has_key("next"):
                self.res[Y[i]]["next"] = {}
            if i < len_data - 1:
                x_res = self._calcX(X[i+1])
                if x_res > 0:
                    if self.res[Y[i]].has_key("next_up"):
                        self.res[Y[i]]["next_up"] += x_res
                    else:
                        self.res[Y[i]]["next_up"] = x_res
                else:
                    if self.res[Y[i]].has_key("next_sell"):
                        self.res[Y[i]]["next_sell"] += x_res
                    else:
                        self.res[Y[i]]["next_sell"] = x_res
                if self.res[Y[i]]["next"].has_key(Y[i+1]):
                    self.res[Y[i]]["next"][Y[i+1]] += 1
                else:
                    self.res[Y[i]]["next"][Y[i+1]] = 1
                    
            # statistics up and sell
            x_res = self._calcX(X[i])
            if x_res > 0:
                self.res[Y[i]]["up"] += 1
                self.res[Y[i]]["up_sum"] += x_res
            elif x_res < 0:
                self.res[Y[i]]["sell"] += 1
                self.res[Y[i]]["sell_sum"] += x_res
                
            # all info
            self.res[Y[i]]["sum"] += x_res
            self.res[Y[i]]["ct"] += 1
            total_ct += 1
            
        for i in range(self.n):
#            print self.res[i]["up"], self.res[i]["sell"]
            self.res[i]["ct_per"] = self.res[i]["ct"] * 1.0 / total_ct
            self.res[i]["center"] = centers[i]
            if self.res[i]["ct"] > 0:
                self.res[i]["up_per"] = -1
                if (self.res[i]["up"] + self.res[i]["sell"]) > 0:
                    self.res[i]["up_per"] = self.res[i]["up"] * 100.0 / (self.res[i]["up"] + self.res[i]["sell"])
                self.res[i]["E"] = self.res[i]["sum"] * 1.0 / (self.res[i]["ct"])
                for j in range(self.n):
                    if self.res[i]["next"].has_key(j):
                        self.res[i]["next"][j] = self.res[i]["next"][j] * 1.0 / self.res[i]["ct"]
        
#        for i in range(self.n):
#            for j in range(self.n):
#                if self.res[i].has_key("next") and self.res[i]["next"].has_key(j):
#                    self.res[i]["next"][j] -= self.res[j]["ct_per"]
                    
        for i in range(self.n):
            self.res[i]["next_e"] = 0
            self.res[i]["center_up"] = 0
            for j in range(self.n):
                if self.res[i].has_key("next") and self.res[i]["next"].has_key(j):
                    if self.res[i]["next"][j] > 0:
                        if self.diffCenter(self.res[i]["center"], self.res[j]["center"]):
                            self.res[i]["center_up"] += 1
                        self.res[i]["next_e"] += self.res[i]["next"][j] * self.res[j]["E"]
        return self.res
    
    def diffCenter(self, father, child):
        return father[0] < child[0]
    
    def mkPredictVec(self):
        vec = []
        for i in range(self.n):
            vec.append([i, self.res[i]["ct"], self.res[i]["next_e"]])
        return vec
    
    def printOut(self):
        for i in range(self.n):
            print "----------------", i, "----------------"
            print "sum: ", self.res[i]["sum"]
            print "up sum: ", self.res[i]["up_sum"], 
            print "sell sum: ", self.res[i]["sell_sum"]
            print "count: ", self.res[i]["ct"]
            print "count_per: ", self.res[i]["ct_per"]
            print "up count: ", self.res[i]["up"], 
            print "sell count: ", self.res[i]["sell"]
            print "center: ", self.res[i]["center"]
            print "center_up: ", self.res[i]["center_up"]
            try:
                print "up_per: ", self.res[i]["up_per"]
                print "next: ", self.res[i]["next_e"]
                print "next up: ", self.res[i]["next_up"],
                print "next sell: ", self.res[i]["next_sell"]
#                for k in self.res[i]["next"].keys():
#                    print "  ", k, ": ", self.res[i]["next"][k]
            except:
                1
                
    def _calcX(self, vec):
        res = 0
        for one in vec:
            res += one
        return res

class ClusterTesterMarket(ClusterTester):
    def _calcX(self, vec):
        return vec[2]
    
if __name__ == "__main__":
    print "Hello World";
