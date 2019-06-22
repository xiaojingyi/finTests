#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-7 19:21:52$
# Note: This source file is NOT a freeware
# Version: np_test.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-7 19:21:52$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np

def predict():
    from sklearn import linear_model
    X = [[0, 2., 4, 3], [1., 2., 3, 9], [2., 4., 6, 0], [3., 9., 8, 11]]
    Y = [3, 8, -2, 8]
    clf = linear_model.BayesianRidge()
    clf.fit(X, Y)
    print clf.predict([[2,5,4,1.5]])

def main():
    predict()
    return

if __name__ == "__main__":
    main()
