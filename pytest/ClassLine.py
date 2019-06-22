#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-6 16:01:20$
# Note: This source file is NOT a freeware
# Version: Line.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-6 16:01:20$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from lib.Util import *

POINT_N = 80

class LineUnZero(object):
    def defautConf(self):
        return {
            "e_n": 100,
            "point_n": 10,
            "round": False,
        }
        
    def __init__(self, config):
        if config:
            self.config = config
        else:
            self.config = self.defaultConf()
            
        self.e_avg = self.e_avg_h = self.e_avg_l = 0
        self.n_last = 0
        self.max = 0
        self.min = 10000
        self.status = self.status_last = self.status_walk = 0
        self.freq = self.ct = 0
        self.break_line = False
        self.ct_h = self.ct_l = self.ct_hl = 0
        
    def add(self, n):
        if self.config["round"]:
            n = round(n, 0)
        
        self.mm(n)
        self.avg(n)
        self.st(n)
        
        self.n_last = n
        self.ct += 1
#        print  self.ct_h
        return [
            n, self.e_avg, self.e_avg_l, 
            self.e_avg_h, self.break_line, self.ct_hl,
            self.ct_l, self.ct_h,
            ]
    
    def st(self, n):
        if n < self.e_avg_l:
            self.status = -2
            self.setBreakFlag(self.n_last > self.e_avg_l)
        elif n > self.e_avg_h:
            self.status = 2
            self.setBreakFlag(self.n_last < self.e_avg_h)
        elif n < self.e_avg:
            self.status = -1
            self.setBreakFlag(self.n_last > self.e_avg)
            self.ct_l += n - self.e_avg
            self.ct_hl = 0
        elif n > self.e_avg:
            self.status = 1
            self.setBreakFlag(self.n_last < self.e_avg)
            self.ct_h += n - self.e_avg
            self.ct_hl += n - self.e_avg
        
        if self.status_last == -2 and self.status == -1:
            self.status_walk = 1
        elif self.status_last == -1 and self.status == 1:
            self.status_walk = 2
        elif self.status_last == 1 and self.status == 2:
            self.status_walk = 3
        elif self.status_last == 2 and self.status == 1:
            self.status_walk = -1
        elif self.status_last == 1 and self.status == -1:
            self.status_walk = -2
        elif self.status_last == -1 and self.status == -2:
            self.status_walk = -3

        self.status_last = self.status
        
    def avg(self, n):
        self.e_avg = EAvg(self.e_avg, n, self.config["e_n"])
        if n > self.e_avg:
            self.e_avg_h = EAvg(self.e_avg_h, n, self.config["e_n"])
        elif n < self.e_avg:
            self.e_avg_l = EAvg(self.e_avg_l, n, self.config["e_n"])

    def mm(self, n):
        if self.max < n:
            self.max = n
        if self.min > n:
            self.min = n
            
    def setBreakFlag(self, exp=False):
        if exp:
            self.break_line = True
        else:
            self.break_line = False
            
class Line(object):
    global POINT_N
    
    e_n = 100
    a = 2 / (e_n + 1)
    i = 0
    point_n = POINT_N
    static_point = 0
    round = False
    
    max = 0
    min = 1000000
    avg = 0
    e_avg = 0
    e_up_avg = 0
    e_down_avg = 0
    point = 1
    last_n = 0
    status_prev = 0
    status = 0 # -2, -1, 1, 2
    walk_status = 0 # -3, -2, -1, 1, 2, 3
    walk_score = 0
    
    def __init__(self, e_n=100, point_n = POINT_N):
        self.point_n = point_n
        self.e_n = e_n
        self.a = 2.0 / (e_n + 1)
        return
    
    def info(self):
        ret = {
            "last_n": self.last_n,
            "max": self.max,
            "min": self.min,
            "avg": self.avg, 
            "e_avg": self.e_avg,
            "point": self.point,
        }
        return ret
    
    def config(self, data):
        if data.has_key("static_point"):
            self.static_point = self.point = data["static_point"]
        if data.has_key("round"):
            self.round = data["round"]
        
    def add(self, n):
        if self.round:
            n = round(n, 0)
        self.i += 1
        self._avg(n)
        self._minMax(n)
        self._status(n)
        if abs(n - self.last_n) > self.point:
            walk = n - self.last_n
            self.last_n = n
            return self.last_n, walk
        else:
            return self.last_n, 0
#        return self.walk_score
        
    def _minMax(self, n):
        if self.max < n:
            self.max = n
        if self.min > n:
            self.min = n
        if n > 0:
            self.e_up_avg = self.e_up_avg * (1 - self.a) + self.a * n
        elif n < 0:
            self.e_down_avg = self.e_down_avg * (1 - self.a) + self.a * n
        
        if self.static_point == 0:
            self.point = (self.e_up_avg - self.e_down_avg) * 1.0 / self.point_n
        else:
            self.point = self.static_point
        
    def _status(self, n):
        if n < self.e_down_avg:
            self.status = -2
        elif n > self.e_up_avg:
            self.status = 2
        elif n < 0:
            self.status = -1
        elif n > 0:
            self.status = 1
        
        if self.status_prev == -2 and self.status == -1:
            self.walk_status = 1
            self.walk_score = 1
        elif self.status_prev == -1 and self.status == 1:
            self.walk_status = 2
            self.walk_score = 2
        elif self.status_prev == 1 and self.status == 2:
            self.walk_status = 3
            self.walk_score = 1
        elif self.status_prev == 2 and self.status == 1:
            self.walk_status = -1
            self.walk_score = -1
        elif self.status_prev == 1 and self.status == -1:
            self.walk_status = -2
            self.walk_score = -2
        elif self.status_prev == -1 and self.status == -2:
            self.walk_status = -3
            self.walk_score = -1

        self.status_prev = self.status
        
    def _avg(self, crr_n):
        self.e_avg = self.e_avg * (1 - self.a) + self.a * crr_n
        self.avg = (self.avg * (self.i-1) + crr_n) * 1.0 / self.i
        
def main():
    line = Line(10)
    print line.add(3)
    print line.add(5)
    print line.add(10)
    print line.add(12)
    print line.add(12.2)
    print line.add(11.9)
    print line.add(13.9)
    print line.add(14.3)
    print line.e_n
    print line.point
    print "Hello World";
    
if __name__ == "__main__":
    main()
