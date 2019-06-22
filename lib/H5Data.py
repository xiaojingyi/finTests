#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: H5Data.py
# Date: 2015 2015年06月14日 星期日 10时43分59秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import h5py
import random

# You may need to 'pip install scikit-learn'
import sklearn
import sklearn.datasets
import sklearn.linear_model

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class H5Data(object):
    def __init__(self, conf):
        self.conf = {}
        self.conf = conf
        self.path = conf['path']
        if not os.path.exists(self.path):
            self.bail("path not exists: %s" % self.path)

        self.train_f = os.path.join(self.path, conf['train_f'])
        self.val_f = os.path.join(self.path, conf['val_f'])
    
    def saveLine(self, x, y): # TODO
        total = 10000
        p = random.randint(1, total)
        if p < total / 10:
            with h5py.File(self.val_f, 'a+') as f:
                f['data'] = x
                f['label'] = y.astype(np.float32)
        else:
            with h5py.File(self.train_f, 'a+') as f:
                f['data'] = x
                f['label'] = y.astype(np.float32)
                
    def save(self, X, y):
        X, Xt, y, yt = sklearn.cross_validation.train_test_split(X, y)
        with h5py.File(self.train_f, 'w') as f:
            f['data'] = X
            f['label'] = y.astype(np.float32)
        with h5py.File(self.val_f, 'w') as f:
            f['data'] = Xt
            f['label'] = yt.astype(np.float32)
        print "saved:", self.train_f, self.val_f
        return

    def testPrint(self):
        print "Hello World!"

    def bail(self, msg):
        print msg
        exit()

def main():
    conf = {
            "path": "./",
            "train_f": "train.h5",
            "val_f": "val_f.h5",
            }
    t = H5Data(conf)
    t.save(np.array([[1,2], [2,3]]), np.array([1,2]))
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

