#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-19 14:39:44$
# Note: This source file is NOT a freeware
# Version: indexes_test.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-19 14:39:44$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from InstanceIndexes import *
from InstanceTraining import *

def main():
    global_source_file = "data/XAUUSD1-hst-new.csv"
#    global_source_file = "data/XAUUSD1-hst-train.csv"
    global_source_file = "data/XAUUSD1.csv"
#    global_source_file = "data/XAUUSD60.csv"
#    global_source_file = "data/tick_IF_all.csv"
#    global_source_file = "data/tick_IF/20150311_IF.csv"

#    config = {
#            "src": global_source_file,
#            "cluster_n": 3,
#            "market_pool": 60,
#            "test_src": global_source_file,
##            "test_src": "data/XAUUSD1.csv",
#            "stop_lose": 10,
#            "stop_win": 2000,
#        }
#    index = IndexesMaker(config)
#    index.training()
#    index.check()
#    
    m = np.array([[1,2,3,4,5,6,7,8,9], [9,8,7,6,5,4,3,2,1]])
    m = np.corrcoef(m)
    print m
    
    config = {
            "src": global_source_file,
            "cluster_n": 2,
            "item_len": 1000,
            "train_len": 5,
            "test_len": 50,
            "stop_lose": 1000,
            "stop_win": 2000,
            "lose_move": False,
            "pool_clean": False,
            "mkt_type": "avol",
        }
    t = Training(config)
#    t.check(False)
#    t.check(True)
#    t.afterCheck()
    t.plot()
    return
    
if __name__ == "__main__":
    print "Hello World";
