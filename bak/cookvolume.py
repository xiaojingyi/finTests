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

vol_size = 3000
time_len = 1
price_file = "data/XAUUSD1.csv"
res_file = "volum_xau.csv"
g = 0.01
diff = 0.7
stop_lose = -1.4
stop_win = 100
err_max_ct = 3
err_g = 0.2
crr_deals = []
deals_len = 3
deals_err_max = 2

def getMiniData():
    price_dt = readFileLines(price_file)
    price_info =[]    
    for one in price_dt:
        one = one.split(",")
        open_p = float(one[2])
        high_p = float(one[3])
        low_p = float(one[4])
        close_p = float(one[5])
        vol = float(one[6])
        price_walk = close_p - open_p
        walk_per = price_walk / vol * 1000
        avg_price = (high_p + low_p) / 2
        price_info.append([one[0], one[1], walk_per, price_walk, vol, avg_price])
#        print [one[0], one[1], walk_per, price_walk, vol, avg_price]
    return price_info

def toBigData(data):
    price_info = []
    per_ls = []
    ct = per = vol_all = price_vol = 0
    dt_len = len(data)
    print dt_len
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
#    price_len = len(price_info)
#    step = ceil(dt_len / price_len / 3)
#    print step
#    j = 0
#    line = []
#    for i in range(dt_len):
#        if j < step:
#            j += 1
#        else:
#            line.append([data[i][0], data[i][1]])
#            j = 0
##            print [data[i][0], data[i][1]]
#    res = []
#    j = 0
#    line_len = len(line)
#    for i in range(line_len):
#        if  j < price_len and line[i][0] + line[i][1] >= price_info[j][0] + price_info[j][1]:
#            res.append(price_info[j])
##            print line[i], price_info[j]
#            j += 1
#        else:
#            res.append([line[i][0], line[i][1], 0,0,0])

    return price_info
#    return res
            
def mkRes(data, price_info):
    price_len = len(price_info)
    dt_len = len(data)
    step = ceil(dt_len / price_len / 3)
    print step
    j = 0
    line = []
    for i in range(dt_len):
        if j < step:
            j += 1
        else:
            line.append([data[i][0], data[i][1]])
            j = 0
#            print [data[i][0], data[i][1]]
    res = []
    j = 0
    line_len = len(line)
    for i in range(line_len):
        if  j < price_len and line[i][0] + line[i][1] >= price_info[j][0] + price_info[j][1]:
            res.append(price_info[j])
#            print line[i], price_info[j]
            j += 1
        else:
            res.append([line[i][0], line[i][1], '','',''])
    return res

#def avgPriceLine(data, time_len):
def mkResWithPrice(data, price_info):
    price_len = len(price_info)
    dt_len = len(data)
    step = ceil(dt_len / price_len / 3)
    print step
    j = 0
    line = []
    temp = []
    for i in range(dt_len):
        if j < step:
            j += 1
            temp.append([data[i][5], data[i][4]])
        else:
            vol_all = 0
            price_all = 0
            for one in temp:
                vol_all += one[1]
                price_all += one[0] * one[1]
            avg = price_all / vol_all
#            line.append([data[i][0], data[i][1], avg])
            line.append([data[i][0], data[i][1], data[i][5]])
            j = 0
            temp = []
            temp.append([data[i][5], data[i][4]])
#            print [data[i][0], data[i][1]]
    res = []
    j = 0
    line_len = len(line)
    for i in range(line_len):
        if  j < price_len and line[i][0] + line[i][1] >= price_info[j][0] + price_info[j][1]:
            print line[i], price_info[j]
            res.append([line[i][0], line[i][1], line[i][2], line[i][2]+price_info[j][2]*50])
            j += 1
        else:
            if j >= price_len:
                break
            res.append([line[i][0], line[i][1], line[i][2], line[i][2]+price_info[j][2]*50])
    return res

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
        # with price debug
#        price_info.append([one[0], one[1], (up_avg - down_avg) * price_avg/20 - 1000 + price_avg, price_avg - 1000, one[5]])
#        print [one[0], one[1], (up_avg - down_avg) * price_avg/20 - 1000 + price_avg, price_avg - 1000, one[5]]
        i += 1
        print i
    return price_info

def calcWin(data):
    direction = last_direction = prev_index = 0
    res = []
    profit = win_ct = total_ct = crr_profit = 0
    market_t = 1
    max_profit = 0
    min_profit = 10000
    one_deal = []
    for one in data:
        print one
        index = one[2] + prev_index
        if abs(index) > g:
            if last_direction * index < 0:
                direction = -direction
            if last_direction == 0:
                direction = index / abs(index)
            prev_index = 0
        else:
            if last_direction * index < 0:
                direction = 0
            prev_index = index
        
        # calc start
        if one_deal:
            crr_profit =  (one[3] - one_deal[1]) * one_deal[0] * market_t - diff
#            if one_deal[2] == 0:
#                crr_index = (one_deal[3] * one_deal[5] + one[2]) / (one_deal[5] + 1)
#                prev_deal_index = one_deal[3]
#                if one_deal[0] == 1:
#                    if (prev_deal_index - crr_index) / prev_deal_index > err_g :
#                        one_deal[4] += 1
#    #                else:
#    #                    one_deal[4] = 0
#                if one_deal[4] > err_max_ct:
#                    one_deal[2] = crr_profit
            
            if one_deal[2] == 0:
                if crr_profit < stop_lose:
                    one_deal[2] = stop_lose
                if crr_profit > stop_win:
                    one_deal[2] = stop_win
            
        if last_direction != direction:
            if last_direction == 0:
                # direction price, out_price, index, err_ct, index_ct
                one_deal = [direction, one[3], 0, one[2], 0, 1]
            else:
                # clean deal
                print one_deal, one[3]
                profit_t = (one[3] - one_deal[1]) * one_deal[0] * market_t - diff
                if one_deal[2] != 0:
                    profit_t = one_deal[2]
                # store into deals
                crr_deals.append(profit_t / abs(profit_t))
                if len(crr_deals) > deals_len:
                    del crr_deals[0]
                # check deals
                deals_sum = 0
                for one_deal_p in crr_deals:
                    if one_deal_p < 0:
                        deals_sum += 1
                if deals_sum >= deals_err_max:
                    market_t *= -1
                # check end
                profit += profit_t
                one_deal = []
                if profit_t > 0:
                    win_ct += 1
                if max_profit < profit_t:
                    max_profit = profit_t
                if min_profit > profit_t:
                    min_profit = profit_t
                total_ct += 1
                # open new deal
                if direction != 0:
                    one_deal = [direction, one[3], 0, one[2], 0, 1]
        #calc end
        
        last_direction = direction
        res.append([one[0], one[1], direction, one[2], one[3], profit])
    print "win and total: ", win_ct, total_ct
    print "max and min: ", max_profit, min_profit
    print "profit: ", profit
    return res

def main():
    price_mini = getMiniData()
    price_info = toBigData(price_mini)
    print len(price_info)
    final_data = anaPrice(price_info)
#    mkCsvFileWin(res_file, final_data)
    res = calcWin(final_data)
    mkCsvFileWin(res_file, res)
##    mkCsvFileWin(res_file, mkRes(price_mini, final_data))
#    mkCsvFileWin(res_file, mkResWithPrice(price_mini, final_data))
    
    print "done res file"
    
if __name__ == "__main__":
    main()