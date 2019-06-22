#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-3-16 20:37:22$
# Note: This source file is NOT a freeware
# Version: Analyse.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-3-16 20:37:22$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

from math import *
from lib.Util import *
import time
from AnalyseBase import *

PRICE_WALK = 0.03

g_pool = []
g_price_walk = PRICE_WALK
g_pool_info = {"start": 0}

def initPriceWalk(num):
    global g_price_walk
    g_price_walk = num
    return

def giveSig (data):
    global g_pool_info_ls
#    print info
    direction = 0
    if data["status"] == 9:
        info = data["info"]
        detail_diff = data["detail_diff"]
        direction = poolSig(info)
    crr_direction = getCrrDirection()
#    if g_pool_info_ls[-1]["walk"] * crr_direction < 0 and g_pool_info_ls[-2]["walk"] * crr_direction < 0:
##    if g_pool_info_ls[-1]["walk"] * crr_direction < 0:
#        return ["3"]
    
    if direction != 0:
        ret =[]
        if direction == 1:
            ret.append("1")
        elif direction == -1:
            ret.append("2")
        return ret
    return ["0"] # none

def addData(data):
    global g_price_walk, g_pool_info
    global g_pool
    
    price_o = data[9]
    price_c = data[5]
    res = {}
    
    if g_pool_info["start"] == 0:
        g_pool_info["start"] = price_o
#    print price_c - g_pool_info["start"], g_price_walk * price_o
    if abs(price_c - g_pool_info["start"]) < g_price_walk * price_o:
        g_pool.append(data)
        res = {"status": 0, "info": ""}
    else:
        g_pool.append(data)
        pool_len = len(g_pool)
#        print price_c - g_pool_info["start"], g_price_walk * price_o        
        res = {"status": 9, "info": poolInfo(g_pool)}
#        print g_pool
        res["detail"] = []
        calc_len = 5
        if pool_len > calc_len:
            for i in range(calc_len):
                res["detail"].append(poolInfo(g_pool[int(pool_len * (i) / calc_len) : int(pool_len * (i+1) / calc_len)]))

        prev_one = []
        res["detail_diff"] = []
        if not res['info']["walk"]:
            return {}
        direction = res['info']["walk"] / abs(res['info']["walk"])
        for one in res["detail"]:
            tmp = 0
            if prev_one:
                tmp += int((one["all_per"] - prev_one["all_per"]) * direction > 0)
                tmp *= int((one["close"] - prev_one["close"]) * direction > 0)
                res["detail_diff"].append(tmp)
            prev_one = one
        g_pool_info["start"] = price_c
        g_pool = []
    return res
    
def crrSigStatus():
    global g_direction
    return g_direction
