#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: data.py
# Date: 2016 2016年04月05日 星期二 21时25分14秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
import numpy as np
from pyquery import PyQuery as pq
import random
import h5py
import sklearn
import math
import sklearn.datasets
import sklearn.linear_model
import caffe
from sklearn import cluster, datasets
from caffe import layers as L, params as P, to_proto

sys.path.append("/datas/lib/py")
from lib.Util import *
from lib.MyCaffe import *
from lib.RandMat import RandMat

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class data(object):
    def __init__(self, config):
        if not config:
            self.bail(-1, "no config: data init")
        self.config = config
        self.debug = config["debug"]
        #super(data, self).__init__(config)
    
    def run(self):
        src = "../data/XAUUSD1-hst-train.csv"
        src = "../data/XAUUSD60.csv"
        content = getFileContent(src, False)
        lines = content.split("\n")
        lines = map (lambda x: x.split(','), lines)
        lines = map (lambda x: [
            float(x[2]), 
            float(x[3]), 
            float(x[4]), 
            float(x[5]), 
            ], lines)
        l_lines = len(lines)
        split_num = int(l_lines * 0.9)
        i = 0
        feat_len = 100
        future_len = 100
        step = feat_len + future_len

        self.net(4, feat_len)

        X = []
        y = []
        Xt = []
        yt = []
        while i < l_lines:
            tmp = lines[i:i+step]
            if len(tmp) < step:
                break
            t_X = np.array(tmp[0:feat_len]).reshape(feat_len * 4)
            #t_X = self.norm(t_X)
            t_y = tmp[-1][3] - tmp[feat_len][0]
            t_y = self.label(t_y, 1)
            if t_y != 0:
                if i < split_num:
                    X.append(t_X)
                    y.append(t_y)
                else:
                    Xt.append(t_X)
                    yt.append(t_y)
            i += 4
            #print tmp
            #print t_X
            #print t_y
            #break
        del lines
        counter = {}
        for one in y:
            if counter.has_key(one):
                counter[one] += 1
            else:
                counter[one] = 1
        print "train: ", counter
        counter = {}
        for one in yt:
            if counter.has_key(one):
                counter[one] += 1
            else:
                counter[one] = 1
        print "test: ", counter
        print "feat len", len(X[0]), feat_len

        X, y = self.avgSample(X, y)
        X = np.array(X).reshape((len(X),1,1,len(X[0]))).astype(np.float32)
        y = np.array(y).astype(np.float32)
        Xt = np.array(Xt).reshape((len(Xt),1,1,len(Xt[0]))).astype(np.float32)
        yt = np.array(yt).astype(np.float32)
        return

        with h5py.File("train.h5", 'w') as f:
            f['data'] = X
            f['label'] = y
        with h5py.File("test.h5", 'w') as f:
            f['data'] = Xt
            f['label'] = yt
        return

    def net(self, stock_dim, num):
        data, label = dataLayer("./train.txt", "h5")

        dim_nn = 4096
        points = []
        sum_p = stock_dim
        for i in range(num-1):
            points.append(sum_p)
            sum_p += stock_dim
        slices = sliceLayerCustom(data, points)
        fcs = []
        for i in range(0, len(slices)):
            """
            name, top = fcLayer(slices[i], 2, replace="relu", wname=["w_s", "b_s"])
            """
            name, top = fcLayer(slices[i], 128, replace="relu", wname=["w_s", "b_s"])
            top = self.ipp(top, 128, wname=["w_trans0", "b_trans0"])
            name, top = fcLayer(top, 2, replace="relu", wname=["w_e", "b_e"])
            fcs.append(top)
        concat = concatLayer(*fcs)
        fc, top = fcLayer(concat, dim_nn, replace="relu")
        top = self.ipp(top, dim_nn, wname=["w", "b"])
        fc, top = fcLayer(top, dim_nn, replace="relu", dropout=0)
        fc, top = fcLayer(top, dim_nn, replace="relu", dropout=0)
        fc, top = fcLayer(top, 10)
        n = caffe.NetSpec()
        n.loss = lossLayer(top, label, "softmax")
        n.acc = accLayer(top, label)
        saveNet("./sauron_gold.prototxt", n.loss)
        return

    def ipp(self, bottom, num, rep=3, wname=["w", "b"]):
        assert len(wname) == 2
        top = bottom
        for i in range(rep):
            fc, top = fcLayer(top, num, replace="relu", wname=wname)
        return top

    def label(self, y, alpha = 0.00):
        if y > alpha:
            return 1
        elif y < -alpha:
            return 2
        return 0

    def avgSample(self, X, y):
        assert (len(X) == len(y))
        r_X = X[:]
        r_y = y[:]
        print "len X: ", len(r_X)
        print "len y: ", len(r_X)

        counter = {}
        for i in range(len(y)):
            if counter.has_key(y[i]):
                counter[y[i]]["count"] += 1
                counter[y[i]]["feats"].append(X[i])
            else:
                counter[y[i]] = {"count": 1, "feats": [X[i]]}
        max_counter = 0
        for k in counter.keys():
            print k, counter[k]['count']
            if counter[k]['count'] > max_counter:
                max_counter = counter[k]['count']
        print max_counter

        for k in counter.keys():
            diff_num = max_counter - counter[k]['count']
            for j in range(diff_num):
                tmp_i = random.randint(0, counter[k]['count']-1)
                r_X.append(counter[k]['feats'][tmp_i])
                r_y.append(k)
        print "len X: ", len(r_X)
        print "len y: ", len(r_X)
        ls = []
        for i in range(len(r_X)):
            ls.append([r_X[i], r_y[i]])
        random.shuffle(ls)
        r_X = []
        r_y = []
        for one in ls:
            r_X.append(one[0])
            r_y.append(one[1])
        return r_X, r_y

    def norm(self, v):
        r = np.array(v)
        d = math.sqrt(r.dot(r))
        if d == 0:
            r *= 0
        else:
            r = r * 1.0 / d
        return r

    def testPrint(self):
        print "Hello World!"

    def bail(self, sig, msg):
        print sig, ": ", msg
        exit()

def main():
    conf = {
            "debug": True,
            }
    t = data(conf)
    t.run()
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

