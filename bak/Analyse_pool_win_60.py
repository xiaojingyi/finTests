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

VOL_SIZE = 5000
DIFF = 0
G = 1
STOP_LOSE = -5
STOP_STEP = 1
STOP_WIN = 5
E_A = 600
DEAL_START_CT = 7
RISK_COUNT_MAX = 3

g_pool = []
g_pool_info = {"len": 0, "vol_sum": 0, "walk_sum": 0, "up_walk": 0, "down_walk": 0, "up_vol": 0, "down_vol": 0}
g_pool_tsize = 60
g_pool_vsize = 5000
g_history_pool = []
g_crr_deals = []
g_test_deal = []
g_start_i = 0
g_tmp_ct1 = g_tmp_ct2 = g_tmp_ct3 = 0
g_is_opside = 1
g_err_ct = 0
g_direction = [0, 0]
g_ana_type = "time" # use time to analyse, else "vol"

def initAnaType(type):
    global g_ana_type
    g_ana_type = type
    return
    
def initPoolSize(num, type):
    global g_pool_tsize, g_pool_vsize
    if type == "vol":
        g_pool_vsize = num
    elif type == "time":
        g_pool_tsize = num
    return

def addData(data):
    global g_pool_tsize, g_pool_vsize, g_ana_type
    global g_pool
    
    g_pool.append(data)
    crr_pool_len = len(g_pool)
    p_len = 0
    if g_ana_type == "vol": # --TODO
        p_len = g_pool_vsize
    else: # default time
        p_len = g_pool_tsize
        
    if crr_pool_len > p_len:
        del g_pool[0]
        
    return
    
def poolInfo():
    global g_pool
    global g_pool_tsize, g_pool_vsize, g_ana_type

    res = []
    pool_len = len(g_pool)
    if pool_len < g_pool_tsize:
        return res

    per = 0
    walk_all = 0
    walk_up = 0
    walk_down = 0
    vol_all = 0
    vol_up = 0
    vol_down = 0
    price_updown = 0
    high_p = 0
    low_p = 10000
    close_p = 0
    price_e = 0
    dt = ""
    for one in g_pool:
        dt = one[0] + " " + one[1]
        per += one[2] / pool_len
        price_e += one[8]
        price_updown += one[3] / abs(one[3])
        walk_all += one[3]
        vol_all += one[4]
        close_p = one[5]
        if one[6] > high_p:
            high_p = one[6]
        if one[7] < low_p:
            low_p = one[7]
        if one[3] > 0:
            walk_up += one[3]
            vol_up += one[4]
        elif one[3] < 0:
            walk_down += abs(one[3])
            vol_down += one[4]
    res = [dt, "", per, walk_all, vol_all, close_p, high_p, low_p, walk_up, walk_down, vol_up, vol_down, price_updown, price_e]
    return res

def calcPool(): # calc factory
    global g_crr_deals
    res = calcPoolEAvg()
    return res

def crrSigStatus():
    global g_direction
    return g_direction

def addDeal(market_info):
    global g_start_i, g_is_opside
    global g_crr_deals, g_direction
    global DEAL_START_CT
    global DIFF, STOP_LOSE, STOP_WIN
    
    res = False
    if g_start_i > DEAL_START_CT:
        res = addDealEAvg(market_info)
        
    if g_is_opside == -1 and res:
#        print "before:", res
        for i in range(len(res)):
            if res[i] == "1":
                res[i] = "2"
            elif res[i]  == "2":
                res[i] = "1"
#        print "after:", res
    return res

def addDealEAvg(market_info):
    global g_crr_deals, g_start_i

    direction = market_info[3]
    price = market_info[0]

    if direction != 0:
        ret =[]
        if g_crr_deals and g_crr_deals[0] != direction:
                g_crr_deals = [] # clean
        if direction == 1:
            g_crr_deals = [direction, price]
            ret.append("1")
        elif direction == -1:
            g_crr_deals = [direction, price]
            ret.append("2")
        return ret
    return ["0"] # none

g_eavg_info_prev = []
g_maket_info_prev = []
def calcPoolEAvg():
    global E_A, STOP_LOSE, G
    global g_pool_info, g_pool, g_history_pool, g_direction
    global g_eavg_info_prev, g_maket_info_prev, g_start_i
    global g_tmp_ct1, g_tmp_ct2, g_tmp_ct3
    global g_is_opside, g_err_ct

    g_start_i += 1
#    print g_start_i
    mini_line = poolInfo()
#    print len(g_pool)
#    print mini_line
    if not mini_line:
        return False
    
    # [dt, "", per, walk_all, vol_all, close_p, high_p, low_p, walk_up, walk_down, vol_up, vol_down, per_up, per_down]
    mini_per = mini_line[2]
    mini_walk = mini_line[3]
    mini_vol = mini_line[4]
    mini_price = mini_line[5]
    mini_high = mini_line[6]
    mini_low = mini_line[7]
    mini_walk_up = mini_line[8]
    mini_walk_down = mini_line[9]
    mini_vol_up = mini_line[10]
    mini_vol_down = mini_line[11]
    mini_price_updown = mini_line[12]
    price_e = mini_line[13]
    
    eupdown = mini_walk_up - mini_walk_down
    volupdown = mini_vol_up - mini_vol_down
    if mini_vol_up != 0 and mini_vol_down != 0:
        up_down_per = mini_walk_up/mini_vol_up - mini_walk_down/mini_vol_down
    else:
        up_down_per = 0
    if mini_vol > 0:
        all_per = mini_walk / mini_vol
    else:
        all_per = 0
    # 0 price, 1 per, 2 up_down_per, 3 direction, 4 result, 5 all_per, 6 eupdown, 7 volupdown, 8 eprice_chg
    market_info = [mini_price, mini_per, up_down_per, 0, 0, all_per, eupdown, volupdown]
    tmp = mini_per * up_down_per # correct
    tmp2 = mini_per * all_per # same
    tmp3 = mini_per * eupdown # correct
    tmp4 = mini_per * volupdown # err
    tmp5 = mini_per * mini_price_updown
    tmp6 = mini_per * price_e
    
    direction = 0

#    print market_info
#    print tmp, mini_per, up_down_per
    if tmp4 > 0 and tmp3 > 0 and tmp > 0 and tmp5 > 0:# and tmp6 > 0:
#    if tmp6 > 0:
#        print tmp
        direction = mini_per / abs(mini_per)
#        print direction
#    if tmp > 0 and tmp2 > 0 and  tmp3 > 0 and tmp5 > 0:
#        tmp_direction = market_info[1] / abs(market_info[1])
#        direction = tmp_direction
#        g_tmp_ct1 += 1
        
#    print mini_line[0], direction
    market_info[3] = direction
#    if direction != 0:
    if g_direction[0] == market_info[3]:
        g_direction[1] += 1
    else:
        g_tmp_ct1 += g_direction[1] * g_direction[0] * 1
#            print mini_price, ", ", g_direction[0], ", ", g_direction[1], ", ", g_tmp_ct1+1336
        g_direction[0] = market_info[3]
        g_direction[1] = 1

#    if g_direction[0] == market_info[3]:
#        g_direction[1] += 1
#    else:
#        g_direction[0] = market_info[3]
#        g_direction[1] = 1

    return market_info

def calcPoolAvg():
    global g_pool_info, g_pool, g_history_pool
    global g_pool_tsize, g_pool_vsize, g_ana_type
    pool_len = len(g_pool)
    if pool_len < g_pool_tsize:
        print pool_len, g_pool_tsize
        return False

    vol_sum = price_vol = walk_sum = per_sum = 0
    per_ls_up = []
    per_ls_down = []
    for mini_line in g_pool:
        mini_per = mini_line[2]
        mini_walk = mini_line[3]
        mini_vol = mini_line[4]
        mini_price = mini_line[5]
        mini_high = mini_line[6]
        mini_low = mini_line[7]
        if mini_per > 0:
            per_ls_up.append(mini_line)
        elif mini_per < 0:
            per_ls_down.append(mini_line)
        vol_sum += mini_vol
        price_vol += mini_price * mini_vol
        walk_sum += mini_walk
        per_sum += mini_per
    # all info start
    big_price_avg = price_vol / vol_sum
    big_per_vol = walk_sum / vol_sum
    big_per_one = per_sum / g_pool_info['len']
    price_index = mkPricePer(g_pool)
    # all info end
    up_info = mkRangeInfo(per_ls_up)
    down_info = mkRangeInfo(per_ls_down)
    diff_one = up_info['per_one'] + down_info['per_one']
    diff_all = up_info['per_all'] + down_info['per_all']
    up_len = up_info['len']
    down_len = down_info['len']
    up_vol = up_info['vol_sum']
    down_vol = down_info['vol_sum']
    diff_one_per = (up_info['per_one']  * down_len + down_info['per_one']  * up_len) / (up_len+down_len)
    diff_all_per = (up_info['per_all']  * down_vol + down_info['per_all']  * up_vol) / (up_vol+down_vol)
    up_one_len_p = up_len*100/(down_len+up_len)
    up_one_vol_p = up_vol*100/(down_vol+up_vol)

    market_info = [mini_price, price_index, big_per_vol, big_per_one, diff_one, diff_all, diff_one_per, diff_all_per]
    g_history_pool.append(market_info)
    return market_info

def mkRangeInfo(data):
    vol_sum = walk_sum = price_vol = 0
    per_sum = 0
    data_len = len(data)
    for one in data:
        vol_sum += one[4]
        walk_sum += one[3]
        price_vol += one[5] * one[4]
        per_sum += one[2]
    if vol_sum == 0 or data_len == 0:
        return {"per_all": 0, "per_one": 0, "p_avg": 0,"len": 0, "vol_sum": vol_sum, "err": 1}
    per_all = walk_sum / vol_sum
    per_one = per_sum / data_len
    price_avg = price_vol / vol_sum
    return {"per_all": per_all, "per_one": per_one, "p_avg": price_avg, "len": data_len, "vol_sum": vol_sum, "err": 0}

def mkPricePer(data):
    global DIFF
    
    open = close = high = low = 0
    mode = 0 # 1 fist down, 2 first up
    len_data = len(data)
    i = high_i = low_i = 0
    for i in range(len_data):
        if i == 0:
            open = close = high = low = data[i][5]
        else:
            if data[i][6] > high:
                high = data[i][6]
                high_i = i
            if data[i][7] < low:
                low = data[i][7]
                low_i = i
        i += 1
    close = data[i-1][5]
    if low_i < high_i :
        mode = 1
    else:
        mode = 2
        
    walk = close - open
    hl_diff = high  - low
    market_type = 0
    price_index = 0
    if abs(walk) < DIFF or abs(walk) / hl_diff < 0.2:
        market_type = 3 # horizon
    elif walk > 0:
        market_type = 1 # up
        if mode == 1:
            price_index = abs(walk) / hl_diff
        elif mode == 2:
            price_index = abs(walk) / hl_diff / 3
    elif walk < 0:
        market_type = 2 # down
        if mode == 2:
            price_index = -abs(walk) / hl_diff
        elif mode == 1:
            price_index = -abs(walk) / hl_diff / 3
#    print [open, high, low, close, mode, price_index]
    return price_index
