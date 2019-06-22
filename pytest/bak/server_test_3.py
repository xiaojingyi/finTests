#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-3-15 21:54:36$
# Note: This source file is NOT a freeware
# Version: server_test.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2014-12-20 21:17:02$"
import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

from math import *
from lib.Util import *
import time

sleep_set = 0.01
vol_size = 20000
time_len = 1
g = 0
diff = 1
stop_lose = -300
stop_win = 300
crr_deals = []
deals_len = 10000
deals_err_max = 6000
give_opside = -1

one_deal = []
test_data = []
data_index = 0
amount_all = 0

test_file = "data/XAUUSD30.csv"
res_file = "server_test_res.csv"
tmp_data = readFileLines(test_file)
for one in tmp_data:
    tmp_one = one.split(",")
    if tmp_one:
        test_data.append(tmp_one)

def mkMiniLine():
    global test_data, data_index
    one = test_data[data_index]
    data_index += 1
#    print one
    # make mini data
    open_p = float(one[2])
    high_p = float(one[3])
    low_p = float(one[4])
    close_p = float(one[5])
    vol = float(one[6])
    price_walk = close_p - open_p
    
    if price_walk == 0:
        return
    price_walk = price_walk / abs(price_walk)
    price_walk *= high_p - low_p
    
#        walk_per = price_walk*price_walk*price_walk/abs(price_walk) / vol * 1000
    walk_per = price_walk / vol * 1000
    avg_price = (open_p + close_p) / 2
    avg_price = close_p
    mini_line = [one[0], one[1], walk_per, price_walk, vol, avg_price, high_p, low_p]
#    print [one[0], one[1], walk_per, price_walk, vol, avg_price]
    return mini_line

def calcDeal(deal, crr_price):
    global diff
    if deal[2] != 0:
        return deal[2]
    return (crr_price - deal[1]) * deal[0] - diff

opt_ct = 0
order_result = []
test_result = []
win_ct = opt_ct = 0
def sendOrder(sig, price):
    global opt_ct, one_deal, order_result, amount_all, win_ct, opt_ct
    if give_opside:
        one_deal[0] *= -1
        if sig == "1":
            sig = "2"
        elif sig == "2":
            sig = "1"
            
    if sig == "1":
        1
#        order_result.append([one_deal[6], one_deal[7], one_deal[1], price, "buy", 0, amount_all])
    elif sig == "2":
        2
#        order_result.append([one_deal[6], one_deal[7], one_deal[1], price, "sell", 0, amount_all])
    elif sig == "3":
        profit = calcDeal(one_deal, price)
        opt_ct += 1
        if profit > 0:
            win_ct += 1
        amount_all += profit
        order_result.append([one_deal[6], one_deal[7], one_deal[1], price, "clean", profit, amount_all])
        one_deal = []
    return

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
        return {"per_all": 0, "per_one": 1, "p_avg": 0,"len": 0, "vol_sum": vol_sum, "err": 1}
    per_all = walk_sum / vol_sum
    per_one = per_sum / data_len
    price_avg = price_vol / vol_sum
    return {"per_all": per_all, "per_one": per_one, "p_avg": price_avg, "len": data_len, "vol_sum": vol_sum, "err": 0}

def mkPricePer(data):
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
    if abs(walk) < diff * 2 or abs(walk) / hl_diff < 0.2:
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

test_print_index = 0
def testPrint(dt):
    data = dt[:]
    global test_result, test_print_index
    if isinstance(data, dict):
        tmp = []
        for k in data.keys():
            tmp.append(data[k])
        data = tmp
    data.insert(0, test_print_index)
    test_print_index += 1
    print data
    test_result.append(data)
    return

def main():
    global one_deal, order_result, win_ct, opt_ct, amount_all, test_result
    import Analyse
    test_tmp = 0
    while(1):
        if data_index >= len(test_data):
            break
        one = mkMiniLine()
        if not one:
            continue
        
        Analyse.addData(one)
        res = Analyse.calcPool()
        if res:
            1 # none
#            print res
            testPrint(res)
       
    mkCsvFileWin("test_info.csv", test_result)
    print test_tmp
    print "done res file"

if __name__ == "__main__":
    main()
    