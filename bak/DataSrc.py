#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-3-29 10:16:31$
# Note: This source file is NOT a freeware
# Version: DataSrc.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-3-29 10:16:31$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

g_type = "MT4" # also IF(shang zhen), MT4RUN(mt4 real time)
g_fhandle = False

def init(fname, t):
    global g_type, g_fhandle
    g_type = t
    
    if g_type == "MT4":
        if not os.path.isfile(fname):
            print "No such file! " + fname
            return False
        g_fhandle = open(fname, "r")
    elif g_type == "IF":
        if not os.path.isfile(fname):
            print "No such file! " + fname
            return False
        g_fhandle = open(fname, "r")
    else:
        print "init type error! only for: MT4, IF, MT4RUN"
        return False
    return True

def mkData(tmp_arr):
    global g_type, g_fhandle
    res = False
    if g_type == "MT4":
        res = mkDataMT4(tmp_arr)
    elif g_type == "IF":
        res = mkDataMT4(tmp_arr)
    else:
        print "mkdata type error! only for: MT4, IF, MT4RUN"
    return res

def mkDataMT4(one):
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

def getLine():
    global g_type, g_fhandle
    res = False
    while(1):
        if g_type == "MT4":
            res = getLineMT4()
            if not res:
                break
        elif g_type == "IF":
            res = getLineIF()
            if not res:
                break
        else:
            print "getline type error! only for: MT4, IF, MT4RUN"
            break
        res = mkData(res)
        if res:
            break
    return res

def getLineMT4():
    global g_type, g_fhandle
    res = []
    if g_fhandle:
        tmp = g_fhandle.readline()
        if not tmp:
            return False
        res = tmp.split(",")
    else:
        print "file open error!"
        return False
    return res

g_if_prev_data = []
def getLineIF():
    global g_type, g_fhandle
    global g_if_prev_data
    res = []
    if g_fhandle:
        tmp = g_fhandle.readline()
        if not tmp:
            return False
        crr_data = tmp.split(",")
        if not g_if_prev_data:
            g_if_prev_data = crr_data
            tmp = g_fhandle.readline()
            crr_data = tmp.split(",")
        price_o = float(g_if_prev_data[2])
        price_c = float(crr_data[2])
        vol_prev = int(g_if_prev_data[8])
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
        g_if_prev_data = crr_data
    else:
        print "file open error!"
        return False
    return res

def done():
    global g_type, g_fhandle
    if g_fhandle:
        g_fhandle.close()
    return True

if __name__ == "__main__":
    print "Hello World";
