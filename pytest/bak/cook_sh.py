#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2013-8-16 14:41:13$
# Note: This source file is NOT a freeware
# Version: cookgold.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2014-12-20 21:17:02$"
import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

from math import *
from lib.Util import *

vol_size = 10000
time_len = 2
price_file = "data/tick_IF/"
res_file = price_file + ".res.csv"
g = 0.05
diff = 0.2
stop_lose = -1
stop_win = 50

def getMiniData(fname):
    price_dt = readFileLines(fname)
    price_info =[]
    i = pre_vol =  0
    for one in price_dt:
        one = one.split(",")
        crr_price = float(one[2])
        vol_sum = int(one[8])
        if i != 0:
            price_walk = crr_price - pre_price
            vol = vol_sum - pre_vol
            if vol <= 0 or price_walk == 0:
                i += 1
                continue
            avg_price = (crr_price + pre_price) / 2
#            walk_per = price_walk * price_walk * price_walk / abs(price_walk) / vol * 1000
            walk_per = price_walk / vol * 1000
            price_info.append([one[0], one[1], walk_per, price_walk, vol, avg_price])
#            print [one[0], one[1], walk_per, price_walk, vol, avg_price]
        pre_price = crr_price
        pre_vol = vol_sum
        i += 1
    return price_info

def toBigData(data):
    price_info = []
    per_ls = []
    ct = per = vol_all = price_vol = 0
    dt_len = len(data)
#    print dt_len
    for i in range(dt_len):
        one = data[i]
        if vol_all < vol_size:
            per_ls.append([data[i][2], data[i][4]])
            vol_all += data[i][4]
            price_vol += data[i][4] * data[i][5]
            ct +=1 
        else:
#            print vol_all
            for per_one in per_ls:
                per += per_one[0] * per_one[1] / vol_all
#            price_info.append([one[0], one[1], per, one[3], vol_all, price_vol / vol_all])
            price_info.append([one[0], one[1], per, one[3], vol_all, one[5]])
#            print [one[0], one[1], per, one[3], vol_all, one[5]]
            #init
            per_ls = []
            ct = per = vol_all= price_vol = 0
            per_ls.append([data[i][2], data[i][4]])
            vol_all += data[i][4]
            price_vol += data[i][4] * data[i][5]
            ct += 1
    return price_info
   
def anaPrice(data):
    i = 0
    price_info = []
    for one in data:
        up_ls = []
        down_ls = []
        price_ls = []
#        walk_per = one[2]
        for j in range(time_len):
            if i - j >= 0:
#                print data[i-j][2]
                walk_per = float(data[i-j][2])
                price_ls.append([data[i-j][5], data[i-j][4]])
                if walk_per > 0:
                    up_ls.append(walk_per)
                elif walk_per < 0:
                    down_ls.append(abs(walk_per))
        up_len = len(up_ls)
        down_len = len(down_ls)
#        print up_len, down_len
        up_avg = down_avg = 0
        for one_per in up_ls:
            up_avg += one_per / up_len
        for one_per in down_ls:
            down_avg += one_per / down_len
        vol_all = price_vol = 0
        for one_p in price_ls:
            vol_all += one_p[1]
            price_vol += one_p[0] * one_p[1]
        price_avg = price_vol / vol_all
        # without price
        price_info.append([one[0], one[1], (up_avg - down_avg), one[5]])
#        print up_avg, down_avg
        # with price debug
#        price_info.append([one[0], one[1], (up_avg - down_avg) * price_avg/20 - 1000 + price_avg, price_avg - 1000, one[5]])
        i += 1
#        print i
    return price_info

def calcDeal(deal, crr_price):
    if deal[2] != 0:
        return deal[2]
    return (crr_price - deal[1]) * deal[0] - diff

def calcWin(data):
#    # type 3
#    index = prev_index = prev_prev_index = total_ct = win_ct = profit = 0
#    up_err = down_err = 0
#    res = []
#    max_profit = 0
#    min_profit = 10000
#    one_deal = []
#    for one in data:
#        profit_t = 0
#        index = one[2]
#        if len(one_deal) > 0:
#            crr_profit = calcDeal(one_deal, one[3])
#            if one_deal[2] == 0:
#                if crr_profit < stop_lose:
#                    one_deal[2] = stop_lose
#                if crr_profit > stop_win:
#                    one_deal[2] = stop_win
#        if index > 0:
#            if prev_index > 0 and prev_prev_index > 0:
#                if len(one_deal) > 0: # have deal
#                    if one_deal[0] == 1: # buy deal
#                        profit_t = calcDeal(one_deal, one[3])
#                        if profit_t < 0:
#                            if one_deal[0] > 0:
#                                up_err += 1
#                            else:
#                                down_err += 1
#                        one_deal = []
#                # direction price, out_price, index, err_ct, index_ct
#                one_deal = [-1, one[3], 0, index, 0, 1]
#            if prev_index < 0:
#                if len(one_deal) > 0:
#                    if one_deal[0] == -1:
#                        profit_t = calcDeal(one_deal, one[3])
#                        if profit_t < 0:
#                            if one_deal[0] > 0:
#                                up_err += 1
#                            else:
#                                down_err += 1
#                        one_deal = []
#        elif index < 0:
#            if prev_index < 0 and prev_prev_index < 0:
#                if len(one_deal) > 0: # have deal
#                    if one_deal[0] == -1: # sell deal
#                        profit_t = calcDeal(one_deal, one[3])
#                        if profit_t < 0:
#                            if one_deal[0] > 0:
#                                up_err += 1
#                            else:
#                                down_err += 1
#                        one_deal = []
#                # direction price, out_price, index, err_ct, index_ct
#                one_deal = [1, one[3], 0, index, 0, 1]
#            if prev_index > 0:
#                if len(one_deal) > 0:
#                    if one_deal[0] == 1:
#                        profit_t = calcDeal(one_deal, one[3])
#                        if profit_t < 0:
#                            if one_deal[0] > 0:
#                                up_err += 1
#                            else:
#                                down_err += 1
#                        one_deal = []
##        print prev_index, index
##        print one_deal
#        if profit_t != 0:
#            total_ct += 1
#            profit += profit_t
#            if profit_t > 0:
#                win_ct += 1
#            if max_profit < profit_t:
#                max_profit = profit_t
#            if min_profit > profit_t:
#                min_profit = profit_t
#
#        prev_prev_index = prev_index
#        prev_index = index
#        res.append([one[0], one[1], index, one[3], profit])
#    # type 3 end
    # type 1
    index = prev_index = total_ct = win_ct = profit = 0
    up_err = down_err = 0
    res = []
    max_profit = 0
    min_profit = 10000
    one_deal = []
    for one in data:
        profit_t = 0
        index = one[2]
        if len(one_deal) > 0:
            crr_profit = calcDeal(one_deal, one[3])
            if one_deal[2] == 0:
                if crr_profit < stop_lose:
                    one_deal[2] = stop_lose
                if crr_profit > stop_win:
                    one_deal[2] = stop_win
        if index > 0:
            if prev_index > 0 and prev_index < index:
                if len(one_deal) > 0: # have deal
                    if one_deal[0] == 1: # buy deal
                        profit_t = calcDeal(one_deal, one[3])
                        if profit_t < 0:
                            if one_deal[0] > 0:
                                up_err += 1
                            else:
                                down_err += 1
                        one_deal = []
                # direction price, out_price, index, err_ct, index_ct
                one_deal = [-1, one[3], 0, index, 0, 1]
            if prev_index < 0:
                if len(one_deal) > 0:
                    if one_deal[0] == -1:
                        profit_t = calcDeal(one_deal, one[3])
                        if profit_t < 0:
                            if one_deal[0] > 0:
                                up_err += 1
                            else:
                                down_err += 1
                        one_deal = []
        elif index < 0:
            if prev_index < 0 and prev_index > index:
                if len(one_deal) > 0: # have deal
                    if one_deal[0] == -1: # sell deal
                        profit_t = calcDeal(one_deal, one[3])
                        if profit_t < 0:
                            if one_deal[0] > 0:
                                up_err += 1
                            else:
                                down_err += 1
                        one_deal = []
                # direction price, out_price, index, err_ct, index_ct
                one_deal = [1, one[3], 0, index, 0, 1]
            if prev_index > 0:
                if len(one_deal) > 0:
                    if one_deal[0] == 1:
                        profit_t = calcDeal(one_deal, one[3])
                        if profit_t < 0:
                            if one_deal[0] > 0:
                                up_err += 1
                            else:
                                down_err += 1
                        one_deal = []
#        print prev_index, index
#        print one_deal
        if profit_t != 0:
            total_ct += 1
            profit += profit_t
            if profit_t > 0:
                win_ct += 1
            if max_profit < profit_t:
                max_profit = profit_t
            if min_profit > profit_t:
                min_profit = profit_t

        prev_index = index
        res.append([one[0], one[1], index, one[3], profit])
    # type 1 end
#    # type 2
#    direction = last_direction = prev_index = 0
#    res = []
#    profit = win_ct = total_ct = 0
#    max_profit = 0
#    min_profit = 10000
#    one_deal = []
#    for one in data:
#        index = one[2] + prev_index
#        if abs(index) > g:
#            if last_direction * index < 0:
#                direction = -direction
#            if last_direction == 0:
#                direction = index / abs(index)
#            prev_index = 0
#        else:
#            if last_direction * index < 0:
#                direction = 0
#            prev_index = index
#        
#        # calc start
#        if one_deal:
#            crr_profit =  (one[3] - one_deal[1]) * -one_deal[0] - diff
#            if one_deal[2] == 0:
#                if crr_profit < stop_lose:
#                    one_deal[2] = -1
#                if crr_profit > stop_win:
#                    one_deal[2] = 1
#        if last_direction != direction:
#            if last_direction == 0:
#                one_deal = [direction, one[3], 0]
#            else:
#                # clean deal
##                print one_deal, one[3]
#                profit_t = (one[3] - one_deal[1]) * -one_deal[0] - diff
#                if one_deal[2] == -1:
#                    profit_t = stop_lose
#                if one_deal[2] == 1:
#                    profit_t = stop_win
#                profit += profit_t
#                one_deal = []
#                if profit_t > 0:
#                    win_ct += 1
#                if max_profit < profit_t:
#                    max_profit = profit_t
#                if min_profit > profit_t:
#                    min_profit = profit_t
#                total_ct += 1
#                # open new deal
#                if direction != 0:
#                    one_deal = [direction, one[3], 0]
#            res.append([one[0], one[1], direction, profit])
#        #calc end
#        
#        last_direction = direction
#        res.append([one[0], one[1], direction, one[2], profit])
#   #type 2 end
    # profit, winper, total, max, min, up_err, down_err
    print profit, ",", win_ct*100/total_ct, ",", total_ct, ",", max_profit, ",", min_profit, ",", up_err, ",", down_err
    return res

def main():
    fls = walkDir(price_file)
    for one in fls:
#        print one
        fname = one.split("/")
        fname =  fname[-1:][0]
        price_mini = getMiniData(one)
        price_info = toBigData(price_mini)
#        print len(price_info)
        final_data = anaPrice(price_info)
        print fname+",", 
        res = calcWin(final_data)
        res_file = fname + ".res.csv"
        mkCsvFileWin(res_file, res)
#    price_mini = getMiniData(price_file)
#    price_info = toBigData(price_mini)
#    print len(price_info)
#    final_data = anaPrice(price_info)
#    res = calcWin(final_data)
#    mkCsvFileWin(res_file, res)
##    mkCsvFileWin(res_file, mkRes(price_mini, final_data))
#    mkCsvFileWin(res_file, mkResWithPrice(price_mini, final_data))
    
    print "done res file"
    
if __name__ == "__main__":
    main()