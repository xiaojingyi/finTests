#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-29 23:29:38$
# Note: This source file is NOT a freeware
# Version: ClassPool.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-29 23:29:38$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

class Pool(object):
    size = 0
    data = []
    len = 0
    reach_max = False
    def __init__(self, size):
        self.size = size
        self.clean()
    
    def clean(self):
        self.data = []
        self.len = 0
        self.reach_max = False
        
    def add(self, one):
        self.data.append(one)
        self.len += 1
#        print self.len, len(self.data)
        self.isFull()
            
    def isFull(self):
        if self.len >= self.size:
            self.reach_max = True
            return True
        return False
    
    def delOne(self):
        self.len -= 1
        del self.data[0]

    def getData(self, clean_reach = True, clean_num=1):
        ret = self.data[:]
        self.afterAdd(clean_num)
        if clean_reach:
            self.reach_max = False
        return ret
    
    def afterAdd(self, clean_num=1):
        if self.isFull():
            for i in range(clean_num):
                self.delOne()
        return
    
class PoolVol(Pool):
    def __init__(self, size):
        super(PoolVol, self).__init__(size)
        
    def add(self, one):
        self.data.append(one)
        vol = one[4]
        self.len += vol
        self.isFull()
        
    def afterAdd(self):
        while self.isFull():
            self.delOne()

    def delOne(self):
        vol = self.data[0][4]
        self.len -= vol
        del self.data[0]
        
if __name__ == "__main__":
    print "Hello World";
