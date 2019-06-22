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
g_pool_info = {"len": 0, "vol_sum": 0}
g_history_pool = []
g_crr_deals = []
g_test_deal = []
g_start_i = 0
g_tmp_ct1 = g_tmp_ct2 = g_tmp_ct3 = 0
g_is_opside = 1
g_err_ct = 0
g_direction = [0, 0]

def addData(data):
    global VOL_SIZE
    global g_pool_info, g_pool
    
    g_pool.append(data)
    g_pool_info["vol_sum"] += data[4]
    g_pool_info["len"] +=1
#    print g_pool_info, VOL_SIZE
    while g_pool_info["vol_sum"] > VOL_SIZE:
        if  g_pool_info["vol_sum"] - g_pool[0][4] > VOL_SIZE:
            g_pool_info["vol_sum"] -= g_pool[0][4]
            g_pool_info["len"] -=1
            del g_pool[0]
        else:
            break
    return
    
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

def findDirection(market_info):
    global g_test_deal
    global RISK_COUNT_MAX
    
    direction = market_info[3]
    price = market_info[0]
    
    if g_test_deal:
        test_direction = g_test_deal[0]
        profit = (price - g_test_deal[1]) * g_test_deal[0]
        print g_test_deal, direction
        if direction != 0:
            if profit > 0:
                g_test_deal[2] -= 1
                if g_test_deal[0] > 0 and g_test_deal[1] < price:
                    g_test_deal[1] = price
                if g_test_deal[0] < 0 and g_test_deal[1] > price:
                    g_test_deal[1] = price
                    
                if test_direction != direction:
                    g_test_deal[0] = direction
                    g_test_deal[2] = RISK_COUNT_MAX-1
            else:
                g_test_deal[2] += 1
                if test_direction == direction:
                    if g_test_deal[2] > RISK_COUNT_MAX:
                        g_test_deal = [-direction, price, 0]
                        return -100
                else:
                    g_test_deal = [direction, price, RISK_COUNT_MAX-2]
                    if g_test_deal[2] > RISK_COUNT_MAX:
                        g_test_deal[2] = 0
        else:
            if profit <= 0:
                g_test_deal[2] += 1
                if g_test_deal[2] > RISK_COUNT_MAX:
                    g_test_deal = [direction, price, 0] # clean
                    return -100
            else:
                if g_test_deal[0] > 0 and g_test_deal[1] < price:
                    g_test_deal[1] = price
                if g_test_deal[0] < 0 and g_test_deal[1] > price:
                    g_test_deal[1] = price
    else:
        g_test_deal = [direction, price, 0] # direction, price, risk_count
    return direction

def addDealEAvg(market_info):
    global g_crr_deals, g_start_i

#    direction = findDirection(market_info)
    direction = market_info[3]
#    direction = 0
    price = market_info[0]
    predict = market_info[4]

#    tmp = market_info[1] * market_info[2]
#    tmp2 = market_info[1] * market_info[5]
#    tmp3 = market_info[1] * market_info[6]
#    tmp4 = market_info[1] * market_info[7]
#    tmp5 = market_info[1] * market_info[8]
#    
#    if tmp > 0 and tmp2 > 0 and tmp3 > 0 and tmp4 > 0 and tmp5 > 0:
#        direction = market_info[2] / abs(market_info[2])
#        
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
#        else:
#            g_crr_deals = []
#            ret.append("3")
            
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
    mini_line = g_pool[len(g_pool) - 1]
    
    mini_per = mini_line[2]
    mini_walk = mini_line[3]
    mini_vol = mini_line[4]
    mini_price = mini_line[5]
    mini_high = mini_line[6]
    mini_low = mini_line[7]
    
    if not g_eavg_info_prev:
        # 0 price, 1 per, 2 up_per, 3 down_per, 4 walk, 5 vol, 6 all_per, 7 up_price, 8 down_price, 9 up_vol, 10 down_vol, 11 price_chg
        g_eavg_info_prev = [mini_price, mini_per, 0, 0, mini_walk, mini_vol, mini_per, 0, 0, 0, 0, 0]
    else:
        a = 1.0 / (E_A+1)
        price_diff = mini_price - g_eavg_info_prev[0]
        if price_diff > 0:
            g_eavg_info_prev[7] =  a * g_eavg_info_prev[7] + (1-a) * price_diff
            g_eavg_info_prev[9] =  a * g_eavg_info_prev[9] + (1-a) * mini_vol
        elif price_diff < 0:
            g_eavg_info_prev[8] =  a * g_eavg_info_prev[8] + (1-a) * price_diff
            g_eavg_info_prev[10] =  a * g_eavg_info_prev[10] + (1-a) * mini_vol
            
        g_eavg_info_prev[1] = a * g_eavg_info_prev[1] + (1-a) * mini_per
        g_eavg_info_prev[4] = a * g_eavg_info_prev[4] + (1-a) * mini_walk
        g_eavg_info_prev[5] = a * g_eavg_info_prev[5] + (1-a) * mini_vol
        g_eavg_info_prev[6] = g_eavg_info_prev[4] / g_eavg_info_prev[5]
        
        g_eavg_info_prev[11] = a * g_eavg_info_prev[11] + (1-a) * price_diff
        if mini_per > 0:
            g_eavg_info_prev[2] = a * g_eavg_info_prev[2] + (1-a) * mini_per
        elif mini_per < 0:
            g_eavg_info_prev[3] = a * g_eavg_info_prev[3] + (1-a) * mini_per

        g_eavg_info_prev[0] = mini_price
    rs = 1
    if g_eavg_info_prev[8] * g_eavg_info_prev[7] != 0:
        rs = abs(g_eavg_info_prev[7] / g_eavg_info_prev[8])
    rsi = 100*rs/(1+rs)
#    if rsi > 80 or rsi < 20:
#        g_is_opside = -1
#    else:
#        g_is_opside = 1
    eprice_chg = g_eavg_info_prev[11];
    eupdown = g_eavg_info_prev[7] + g_eavg_info_prev[8]
    volupdown = g_eavg_info_prev[9] - g_eavg_info_prev[10]
    # 0 price, 1 per, 2 up_down_per, 3 direction, 4 result, 5 all_per, 6 eupdown, 7 volupdown, 8 eprice_chg
    market_info = [mini_price, g_eavg_info_prev[1], g_eavg_info_prev[2] + g_eavg_info_prev[3], 0, 0, g_eavg_info_prev[6], eupdown, volupdown, eprice_chg]
    tmp = market_info[1] * market_info[2] # correct
    tmp2 = market_info[1] * market_info[5] # same
    tmp3 = market_info[1] * eupdown # correct
    tmp4 = market_info[1] * volupdown # err
    tmp5 = market_info[1] * eprice_chg # correct
    tmp6 = eupdown * volupdown # err
    direction = 0
#    if rsi < 35:
#        direction = 1
#    elif rsi > 75:
#        direction = -1

    if tmp > 0 and tmp2 > 0 and  tmp3 > 0 and tmp5 > 0:
#    if tmp5 > 0 and tmp2 > 0 and tmp < 0 and tmp3 < 0 and tmp4 < 0:
#    if tmp > 0:
#    if mini_walk != 0:
#        direction = mini_walk / abs(mini_walk)
        price_diff = 0
        if g_maket_info_prev:
            price_diff = market_info[0] - g_maket_info_prev[0]
#        tmp_direction = g_is_opside * market_info[2] / abs(market_info[2])
#            tmp_direction = volupdown / abs(volupdown)
        tmp_direction = market_info[1] / abs(market_info[1])
        direction = tmp_direction
        if abs(market_info[1]) > G:
            direction = tmp_direction
        g_tmp_ct1 += 1
        
    market_info[3] = direction
    if direction != 0:
        if g_direction[0] == market_info[3]:
            g_direction[1] += 1
        else:
#            if g_direction[1] > 5:
#                print g_direction[0], ", ", g_direction[1]
            g_direction[0] = market_info[3]
            g_direction[1] = 1
#    # test use correct
#    if g_direction[0] == market_info[3] and market_info[3] != 0:
#        g_direction[1] += 1
#        if g_direction[1] > 5:
#            g_is_opside = -1
#    elif market_info[3] != 0:
#        g_is_opside = 1
##    else:
#        g_direction[0] = market_info[3]
#        g_direction[1] = 1
        
    if g_maket_info_prev:
        price_diff = market_info[0] - g_maket_info_prev[0]
        if g_maket_info_prev[3] * price_diff > 0:
            market_info[4] = 1
            g_tmp_ct2 += 1
            g_tmp_ct3 += 1
            g_err_ct = 0.7 * g_err_ct - 0.3 * 1
        elif g_maket_info_prev[3] * price_diff < 0:
            market_info[4] = -1
            g_tmp_ct2 += 1
            g_err_ct = 0.7 * g_err_ct + 0.3 * 1
        elif price_diff == 0 and g_maket_info_prev[3] != 0:
            1 # none
#            g_tmp_ct2 += 1

#    print g_tmp_ct1, g_tmp_ct2, g_tmp_ct3, g_err_ct, g_is_opside, g_eavg_info_prev[7], g_eavg_info_prev[8]
    if abs(g_err_ct) > 0.7:
#        g_is_opside *= -1
        g_err_ct = 0

    g_maket_info_prev = market_info
    return market_info

def calcPoolAvg():
    global g_pool_info, g_pool, g_history_pool

    if g_pool_info["vol_sum"] < VOL_SIZE:
        print len(g_pool), g_pool_info
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
