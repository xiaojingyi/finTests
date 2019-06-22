#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-7-9 9:32:39$
# Note: This source file is NOT a freeware
# Version: caffe_test.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-7-9 9:32:39$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np

import h5py
import caffe

def help():
    print sys.argv[0], " h5file deploy.prototxt caffemodel"
    exit()
    
def predict(item):
    global net
    res = net.predict(item.reshape(1,len(item),1,1), oversample=True).flatten()
#    print res
    res_dic = {}
    i = 0
    for one in res:
        res_dic[str(i)] = one
        i += 1
    final_res = sorted(res_dic.iteritems(), key=lambda d:d[1], reverse = True )
#    print final_res[0]
    return final_res[0]

if len(sys.argv) < 4:
    help()
    
data = False
label = False
future = False

with h5py.File(sys.argv[1], 'r') as f:
    data = np.array(f['data']).astype(np.float32)
    label = np.array(f['label']).astype(np.float32)
    future = np.array(f['future']).astype(np.float32)

net = caffe.Classifier(sys.argv[2], sys.argv[3])
print data
d_len = len(data)
print d_len
ck = 0
sum = 0
profit = 0
profit_all = 0
res = {}
res_all = {}
for i in range(d_len):
    tmp = predict(data[i])
    c = int(tmp[0])
    p = tmp[1]
    profit_one = abs(future[i])
    profit_all += future[i]
#    print future[i], label[i]
    if p > 0:# and c != 1 and label[i] != 1:
        if c == label[i]:
            ck += 1
            if res.has_key(c):
                res[c] += 1
            else:
                res[c] = 1
            if label[i] != 1:
                profit += profit_one
        else:
            if label[i] != 1:
                profit -= profit_one
        sum += 1
        if res_all.has_key(c):
            res_all[c] += 1
        else:
            res_all[c] = 1
    if i % 100 == 0:
        print i, ck, sum, profit, profit_all
        print res
        print res_all

print res
print res_all
print ck, sum, profit, profit_all