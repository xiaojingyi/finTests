#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-15 18:59:06$
# Note: This source file is NOT a freeware
# Version: ClassDataSrc.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-15 18:59:06$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np

class DataSrc(object):
    type = "MT4"
    fhandle = False
    if_prev_data = []
    
    def __init__(self, fname, t="MT4"):
        self.type = t
        if fname.find("IF") > 0:
            self.type = "IF"
        elif fname.find("USD") > 0:
            self.type = "MT4"
        else:
            self.type = False
            print "init type error! only for: MT4, IF, MT4RUN"
            
        if self.type == "MT4":
            if not os.path.isfile(fname):
                print "No such file! " + fname
            else:
                self.fhandle = open(fname, "r")
        elif self.type == "IF":
            if not os.path.isfile(fname):
                print "No such file! " + fname
            else:
                self.fhandle = open(fname, "r")
        else:
            print "init type error! only for: MT4, IF, MT4RUN"
        self.if_prev_data = []
    
    def mkData(self, tmp_arr):
        res = False
        if self.type == "MT4":
            res = self.mkDataMT4(tmp_arr)
        elif self.type == "IF":
            res = self.mkDataMT4(tmp_arr)
        else:
            print "mkdata type error! only for: MT4, IF, MT4RUN"
        return res
    
    def mkDataMT4(self, one):
        res = False
        open_p = float(one[2])
        high_p = float(one[3])
        low_p = float(one[4])
        close_p = float(one[5])
        vol = float(one[6])
        price_walk = close_p - open_p
        price_percent = price_walk_e = walk_per = 0
        vol_up = vol_sell = 0
        hl_diff = high_p - low_p
        if vol == 0 or hl_diff == 0:
            return False

        price_percent = abs(price_walk) * 1.0 / hl_diff
        if price_walk >0:
            vol_sell = (1 - price_percent) * vol / 2
            vol_up = vol * price_percent + vol_sell
        elif price_walk < 0:
            vol_up = (1 - price_percent) * vol / 2
            vol_sell = vol * price_percent + vol_up
        else:
            vol_up = vol_sell = vol * 1.0 / 2
        price_walk_e = price_walk * (price_percent ** 3)
        walk_per = price_walk / vol * 1000
        res = [
            one[0], one[1], walk_per, 
            price_walk, vol, close_p, 
            high_p, low_p, price_walk_e, 
            open_p, vol_up, vol_sell,
            ]
        return res
    
    def getLine(self):
        res = False
        while(1):
            if self.type == "MT4":
                res = self.getLineMT4()
                if not res:
                    break
            elif self.type == "IF":
                res = self.getLineIF()
                if not res:
                    break
            else:
                print "getline type error! only for: MT4, IF, MT4RUN"
                break
            res = self.mkData(res)
            if res:
                break
        return res
    
    def getLineMT4(self):
        res = []
        if self.fhandle:
            tmp = self.fhandle.readline()
            if not tmp:
                return False
            res = tmp.split(",")
        else:
            print "file open error!"
            return False
        return res
    
    def getLineIF(self):
        res = []
        if self.fhandle:
            tmp = self.fhandle.readline()
            if not tmp:
                return False
            crr_data = tmp.split(",")
            if not self.if_prev_data:
                self.if_prev_data = crr_data
                tmp = self.fhandle.readline()
                crr_data = tmp.split(",")
            price_o = float(self.if_prev_data[2])
            price_c = float(crr_data[2])
            vol_prev = int(self.if_prev_data[8])
            vol_crr = int(crr_data[8])
            if price_o > price_c:
                price_h = price_o
                price_l = price_c
            else:
                price_h = price_c
                price_l = price_o
            vol = vol_crr - vol_prev
            dt = crr_data[1].split(" ")
            res = [dt[0], dt[1], price_o, price_h, price_l, price_c, vol]
            self.if_prev_data = crr_data
        else:
            print "file open error!"
            return False
        return res
    
    def done(self):
        if self.fhandle:
            self.fhandle.close()
        return True
    
class DataMatrix(object):
    def __init__(self, m):
        self.m = m
        self.i = 0
        self.len = len(m)
        
    def getChild(self, n=0):
        vec = []
        if n == 0:
            n = self.len
        for i in range(n):
            line = self.getLine()
            if line:
                vec.append(line)
        return vec
    
    def getLine(self):
        if self.i >= self.len:
            return False
        
        l = self.m[self.i]
        self.i += 1
        l = l.tolist()
        for i in range(len(l)):
            if i > 1:
                l[i] = float(l[i])
        return l
        
class DataMatrixGen(object):
    def __init__(self, config=False):
        if config != False:
            self.config = config
        self.src = DataSrc(self.config["src"])
        self.cache = "caches/" + self.config["src"].replace("/", "_") + ".npy"
#        print self.cache
        self.m = self.getDatas()
        self.len = len(self.m)
        self.i_len = self.config["item_len"]
        self.tr_len = self.config["train_len"]
        self.t_len = self.config["test_len"]
        self.i = 0
        self.is_end = False
    
    def getLine(self):
        if self.is_end:
            return False
        m = self.split(self.i, 1)
        if self.i >= self.len:
            self.is_end = True
        self.i += 1
#        print self.i
        return m.getLine()
    
    def getMs(self, step=1):
        if self.is_end:
            return False
        tr_i = self.i
        tr_len = self.i_len * self.tr_len
        t_i = tr_i + tr_len
        t_len = self.i_len * self.t_len
        
        m_tr = self.split(tr_i, tr_len)
        m_t = self.split(t_i, t_len)
        
        if self.i + tr_len + t_len >= self.len:
            self.is_end = True
            
        self.i += step
        return {
            "tr": m_tr,
            "t": m_t,
        }
        
    def getDatas(self):
        datas = []
        try:
            datas = np.load(self.cache)
        except:
            while(1):
                one = self.src.getLine()
                if not one:
                    break
                datas.append(one)
            datas = np.array(datas)
            np.save(self.cache, datas)
        self.src.done()
        return datas

    def split(self, i, n=1):
        return DataMatrix(self.m[i:i+n])
    
if __name__ == "__main__":
    config = {
            "src": "data/XAUUSD60.csv",
            "item_len": 60,
            "train_len": 200,
            "test_len": 50,
        }
    dmg = DataMatrixGen(config)
    print len(dmg.m)
    i = 0
    while(True):
        tmp = dmg.getLine()
        if not tmp:
            break
        print tmp
        i += 1
    print i
#    dm = dmg.split(2092591, 3)
#    print dm.getLine()
#    print dm.getLine()
#    print dm.getLine()
#    print dm.getLine()
    print "Hello World";
