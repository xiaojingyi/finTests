#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-6-15 1:23:40$
# Note: This source file is NOT a freeware
# Version: InstanceDnn.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-6-15 1:23:40$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np
from Instance import *
from ClassFeature import ClassFeature
import h5py
import sklearn
import sklearn.datasets
import sklearn.linear_model

class InstanceDnn(Instance):
    def __init__(self, config):
        if not config:
            self.bail(-1, "no config: InstanceDnn init")
        self.config = config
        self.debug = config["debug"]
        self.label_info = {}
        super(InstanceDnn, self).__init__(config)
        
    def loopData(self, one):
        self.pool_price.add(one)
        if self.pool_price.isFull():
            data = False
            if self.config["pool_clean"]:
                data = self.pool_price.getData(True, self.config['future_sizes'])
            else:
                data = self.pool_price.getData(True)
#                self.pool_price.afterAdd()
            future_data_m = self.loop_data.split(self.loop_data.i, self.config["future_sizes"])
            future_datas = future_data_m.getChild()
            try:
                future_walk = future_datas[-1][5] - future_datas[0][9]
            except:
                print "except"
                future_walk = 0
            future_walk_per = future_walk / data[0][9]
            if abs(future_walk) >= 0:
                feature = ClassFeature({"debug": True});
                feature.setData(data)
                features = feature.feature()
#                diff_walk = abs(future_walk) > abs(feature.price['walk'])
                label = feature.setLabel(future_walk)
                self.labelCount(label)
    #            print features, label
    #            print future_walk, future_walk / features[0]
    #            exit()
                if not features:
                    return
#                features.extend([future_walk])
                self.X.append(features)
#                print self.X
#                print len(features)
#                exit()
                self.y.append([label, future_walk_per])
    #            print label
        return
    
    def mkSrc(self):
        self.X = []
        self.y = []
        self.pool_price = Pool(self.config['item_len'])
        self.dataLoop(1000, self.loopData, self.config["src"], 0, 5000000)
        X, Xt, y, yt = sklearn.cross_validation.train_test_split(self.X, self.y, test_size=0.2)
        X = np.array(X)
        Xt = np.array(Xt)
        y = np.array(y)
        yt = np.array(yt)
        clf = sklearn.linear_model.SGDClassifier(
            loss='log', n_iter=10000, penalty='l2', alpha=1e-1, class_weight='auto')

        print X.shape, len(self.y)
        print self.label_info
        sum_l = 0
        for k in self.label_info.keys():
            sum_l += self.label_info[k]
        print sum_l
        for k in self.label_info.keys():
            print k, self.label_info[k] * 1.0 / sum_l
#        clf.fit(X, y[:,0])
#        yt_pred = clf.predict(Xt)
#        print('Accuracy: {:.3f}'.format(sklearn.metrics.accuracy_score(yt, yt_pred)))
        
        dirname = os.path.abspath(self.config['h5data'])
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        train_filename = os.path.join(dirname, 'train.h5')
        test_filename = os.path.join(dirname, 'test.h5')
        val_filename = os.path.join(dirname, 'validate.h5')

        # HDF5DataLayer source should be a file containing a list of HDF5 filenames.
        # To show this off, we'll list the same data file twice.
        print y[:, 0], y[:, 1]
        print X
        with h5py.File(train_filename, 'w') as f:
            f['data'] = X.astype(np.float32)
#            f['label'] = y[:, 0].astype(np.float32)
            f['label'] = y[:, 1].astype(np.float32)
        with open(os.path.join(dirname, 'train.txt'), 'w') as f:
            f.write(train_filename + '\n')

        # HDF5 is pretty efficient, but can be further compressed.
        comp_kwargs = {'compression': 'gzip', 'compression_opts': 1}
        with h5py.File(test_filename, 'w') as f:
            f['data'] = Xt.astype(np.float32)
#            f['label'] = yt[:, 0].astype(np.float32)
            f['label'] = yt[:, 1].astype(np.float32)
            
        with h5py.File(val_filename, 'w') as f:
            f['data'] = Xt.astype(np.float32)
            f['label'] = yt[:, 0].astype(np.float32)
            f['future'] = yt[:, 1].astype(np.float32)
        
#            f.create_dataset('data', data=Xt.astype(np.float32), **comp_kwargs)
#            f.create_dataset('label', data=yt.astype(np.float32), **comp_kwargs)
        with open(os.path.join(dirname, 'test.txt'), 'w') as f:
            f.write(test_filename + '\n')
        return
    
    def labelCount(self, class_i):
        if self.label_info.has_key(class_i):
            self.label_info[class_i] += 1
        else:
            self.label_info[class_i] = 1
        return class_i
    
    def bail(self, sig, msg):
        print sig, ": ", msg
        exit()
        
    def test(self):
        print "debug: ", self.debug
        
def main():
    config = {
#        "src": "data/XAUUSD1-hst-new.csv",
#        "src": "data/XAUUSD1.csv",
        "src": "data/XAUUSD60.csv",
#        "test_src": "data/XAUUSD1.csv",
#        "test_src": "data/XAUUSD60.csv",
        "h5data": "./h5data",
        "debug": True,
        "stop_lose": 1000,
        "stop_win": 1000,
        "mkt_type": "time",
        "item_len": 30,
        "future_sizes": 4,
        "pool_clean": True,
    }
    model = InstanceDnn(config)
    model.mkSrc()
    return

if __name__ == "__main__":
    main()
