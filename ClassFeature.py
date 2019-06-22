#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-6-23 23:04:45$
# Note: This source file is NOT a freeware
# Version: ClassFeature.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-6-23 23:04:45$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np
import random

class ClassFeature(object):
    def __init__(self, config):
        if not config:
            self.bail(-1, "no config: ClassFeature init")
        self.config = config
        self.debug = config["debug"]
        #super(ClassFeature, self).__init__(config)
    
    def setData(self, data):
        self.data = data
        self.price = {
            "start": data[0][9],
            "walk": data[-1][5] - data[0][9],
            "high": 0,
            "low": 10000,
            "high_i": 0,
            "low_i": 0,
        }
        self.vol = {
            "sum": 0,
            "high": 0,
            "low": 0,
        }
        self.walk = {
            "sum": 0,
            "high": 0,
            "low": 0,
        }
        
        i = 0
        self.features_price_chg = []
        self.features_walk_chg = []
        self.features_vol_chg = []
        self.forces = []
        self.last_info = {
            "walk": 0,
            "price_o":0,
            "price_c":0,
            "vol": 0,
        }
        for one in self.data:
            self.features_price_chg.append((one[5] - self.price['start']) * 1.0 / self.price['start'])
            self.calc(one, i)
            i += 1
        self.features_price_sort = sorted(self.features_price_chg)
        self.force_sort = sorted(self.forces)
        
    def feature(self):
        self.features = [
#            self.price['start'], 
#            self.price['walk'] * 1.0 / self.price['start'], 
#            (self.price['high'] - self.price['start']) * 1.0 / self.price['start'], 
#            (self.price['low'] - self.price['start']) * 1.0 / self.price['start'], 
#            self.price['high_i'], 
#            self.price['low_i'], 
#            
#            self.vol['sum'], 
#            self.vol['high'] * 1.0 / self.vol['sum'], 
#            self.vol['low'] * 1.0 / self.vol['sum'], 
#            
#            self.walk['sum'], 
#            self.walk['high'] * 1.0 / self.walk['sum'], 
#            self.walk['low'] * 1.0 / self.walk['sum'], 
        ]
#        print self.features
#        print self.features_price_chg
#        print self.features_price_sort
        self.features.extend(self.features_price_chg)
#        self.features.extend(self.force_sort)
#        self.features.extend(self.forces)
#        print "features len: ", len(self.features)
        return self.features
            
    def calc(self, one, i):
#        self.forces.append(one[3] - self.last_info['walk'])
        tmp = 0
        if one[3] != 0 and self.last_info['vol'] > 0:
            tmp = (one[3] - self.last_info['walk']) * abs(one[4] * self.last_info['walk'] / one[3] / self.last_info['vol'])
        if one[3] > 1:
            tmp = random.randint(1,10)
        else:
            tmp = random.randint(1,10)
#        self.forces.append(one[3])
#        self.forces.append(tmp)
#        tmp = 
        self.forces.append((one[3] - self.last_info['walk'])*(one[3]))
        self.features_walk_chg.append(one[3])
        self.features_vol_chg.append(one[4])
        self.walk['sum'] += abs(one[3])
        self.vol['sum'] += abs(one[4])
        if self.price['high'] < one[6]:
            self.price['high'] = one[6]
            self.price['high_i'] = i
            self.vol['high'] = self.vol['sum']
            self.walk['high'] = self.walk['sum']
        elif self.price['low'] > one[7]:
            self.price['low'] = one[7]
            self.price['low_i'] = i
            self.vol['low'] = self.vol['sum']
            self.walk['low'] = self.walk['sum']
        # last info
        self.last_info['vol'] = one[4]
        self.last_info['walk'] = one[3]
        self.last_info['price_o'] = one[9]
        self.last_info['price_c'] = one[5]
            
    def setLabel(self, walk):
#        return int(walk)
        jg = 0.55
#        jg = 1
#        return int(walk)
#        walk = abs(walk)
#        if walk >= 0:
#            return 1
#        if walk < 0:
#            return 2
        if walk >= jg:
            return 0
        if walk <= -jg:
            return 2
#        else:
#            return random.randint(3,5)
        return 1
    
    def bail(self, sig, msg):
        print sig, ": ", msg
        exit()
        
    def test(self):
        print "debug: ", self.debug
        
def main():
    config = {
        "debug": True,
    }
    model = ClassFeature(config)
    model.test()
    return

if __name__ == "__main__":
    main()

#import lmdb
#db = lmdb.Environment('./train_lmdb/',readonly = True)
#with db.begin( write = False) as txn:
#    cursor = txn.cursor()
#    for idx, datas in enumerate( cursor.iternext_nodup()):
#            print idx, datas