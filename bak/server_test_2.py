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
give_opside = 0

one_deal = []
test_data = []
data_index = 0
amount_all = 0

test_file = "data/XAUUSD1.csv"
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
#        walk_per = price_walk*price_walk*price_walk/abs(price_walk) / vol * 1000
    walk_per = price_walk / vol * 1000
    avg_price = (high_p + low_p) / 2
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
def testPrint(data):
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
    mini_line = []
    vol_sum = per = price_vol = walk_sum = per_sum = 0
    per_ls_up = []
    per_ls_down = []
    crr_ls = []
    index = prev_index = prev_price = price = 0
    test_tmp = 0
    while(1):
        if data_index >= len(test_data):
            break
        one = mkMiniLine()
        if not one:
            continue
        
        mini_line = one
        if prev_price == 0:
            prev_price = mini_line[5]
        mini_per = mini_line[2]
        mini_walk = mini_line[3]
        mini_vol = mini_line[4]
        mini_price = mini_line[5]
        mini_high = mini_line[6]
        mini_low = mini_line[7]
        
#        print mini_line
        # make big data start ------------------------------------
        crr_ls.append(mini_line)
        if mini_per > 0:
            per_ls_up.append(mini_line)
        elif mini_per < 0:
            per_ls_down.append(mini_line)
        vol_sum += mini_vol
        price_vol += mini_price * mini_vol
        walk_sum += mini_walk
        per_sum += mini_per
        if vol_sum > vol_size:
            # all info start
            big_price_avg = price_vol / vol_sum
            big_per_vol = walk_sum / vol_sum
            big_per_one = per_sum / len(crr_ls)
            price_index = mkPricePer(crr_ls)
            # all info end
#            print mini_line[0], vol_sum
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
            
#            if diff_one > 0:
#                diff_one = 0.001
#            elif diff_one < 0:
#                diff_one = -0.001
            if price_index * diff_one_per < 0:
                test_tmp += 1
            
            # calc 1 start ------------------------------------------------------------------------------------------------------------
            opt_index = price_index * 100
            if price_index > 0:
                direction = 1
            elif price_index < 0:
                direction = -1
            else:
                direction =0
            if big_per_vol * direction < 0:
                opt_index -= 100 * direction
            if big_per_one * direction < 0:
                opt_index -= 100 * direction
            if diff_one * direction < 0:
                opt_index -= 40 * direction
            if diff_all * direction < 0:
                opt_index -= 40 * direction
            if diff_one_per * direction < 0:
                opt_index -= 25 * direction
            if diff_all_per * direction < 0:
                opt_index -= 25 * direction
            opt_now = 0
            if direction > 0 and opt_index > 0:
                opt_now = 1
            if direction < 0 and opt_index < 0:
                opt_now = -1
#            market_info = [mini_line[0], mini_line[0], price_index, big_per_vol, big_per_one, diff_one, diff_all, diff_one_per, diff_all_per]
            market_info = [direction, opt_index, mini_price, opt_now, price_index, big_per_vol, big_per_one, diff_one, diff_all, diff_one_per, diff_all_per]
            testPrint(market_info)
#            if index > 0:
#                if len(one_deal) > 0: # have deal
#                    if one_deal[0] == 1: # sell deal clean
#                        sendOrder("3", mini_line[5])
#                if index - g > 0:
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [-1, ana_line[3], 0, index, 0, 1, mini_line[0], mini_line[1]]
#                        sendOrder("2", mini_line[5])
#            elif index < 0:
#                if len(one_deal) > 0: # have deal
#                    if one_deal[0] == -1: # buy deal clean
#                        sendOrder("3", mini_line[5])
#                if index + g < 0:
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [1, ana_line[3], 0, index, 0, 1, mini_line[0], mini_line[1]]
#                        sendOrder("1", mini_line[5])
            # calc 1 end ------------------------------------------------------------------------------------------------------------
            #init
            per_ls_up = []
            per_ls_down = []
            crr_ls = []
            per = vol_sum = price_vol = walk_sum = per_sum = 0
        # make big data end ------------------------------------
        # stop lose start
#        if len(one_deal):
#            if one_deal[0] == 1:
#                if one[7] - one_deal[1] - diff < stop_lose:
#                    sendOrder("3", mini_line[5])
#            elif one_deal[0] == -1:
#                if one_deal[1] - diff - one[6] < stop_lose:
#                    sendOrder("3", mini_line[5])
        # stop lose end
#        time.sleep(sleep_set)
#    mkCsvFileWin(res_file, order_result)
#    print "winper, lose: ", win_ct * 100 / opt_ct, opt_ct
#    print "all: ", amount_all
    mkCsvFileWin("test_info.csv", test_result)
    print test_tmp
    print "done res file"

if __name__ == "__main__":
    main()
    