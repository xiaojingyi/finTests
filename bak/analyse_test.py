#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-13 22:10:47$
# Note: This source file is NOT a freeware
# Version: analyse_test.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-13 22:10:47$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from InstantAnalyse import *
from ClassPredict import *
import numpy as np

def main():
    global_source_file = "data/XAUUSD1-hst-new.csv"
#    global_source_file = "data/XAUUSD1.csv"
#    global_source_file = "data/XAUUSD60.csv"
#    global_source_file = "data/tick_IF_all.csv"
#    global_source_file = "data/tick_IF/20150311_IF.csv"
    conf = {
        "src": global_source_file,
        "cluster_n": 10,
        "p": PredictMarket,
        "p_pool_size": 20,
        "stop_lose": 1000,
        "stop_win": 2000,
        "market_pool": 600,
    }
    ins = AnalyseMarket()
    ins.conf(conf)
    y1, v1 = ins.trainning()
    index_price = np.load("index_price.npy").transpose()
    print index_price
    index_price.dtype = "float64"
    print np.corrcoef(index_price)
#    conf["src"] = "data/XAUUSD1.csv"
#    ins = AnalyseMarket()
#    ins.conf(conf)
#    y2, v2 = ins.run()
##    for i in range(len(y1)):
###        print y1[i], y2[i]
##        print v1[i], v2[i]


    return

if __name__ == "__main__":
    print "Hello World";
