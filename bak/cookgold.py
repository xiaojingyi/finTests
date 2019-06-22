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

from lib.Util import *
#GOLD
price_file = "data/XAUUSD30.csv"
pos_file = "data/position.csv"
res_file = "res.csv"
# EUR
#price_file = "data/EURUSD30.csv"
#pos_file = "data/poseur.csv"
#res_file = "reseur.csv"
# silver
#price_file = "data/XAGUSD30.csv"
#pos_file = "data/posxag.csv"
#res_file = "resxag.csv"

per_range = 0.33
week_range = 3

def posInfo():
    pos_dt = readFileLines(pos_file)
    pos_info = []
    index = 0
    for one in pos_dt:
        one = one.split(",")
        tmp = {}
        tmp['date'] = one[0]
        tmp['c_buy'] = int(one[1]) # ¶þ×¯¼Ò Âò
        tmp['c_sell'] = int(one[2])
        tmp['f_buy'] = int(one[3]) # ´ó×¯¼Ò Âò
        tmp['f_sell'] = int(one[4])
        if index > 0:
            tmp['c_buy_chg'] = tmp['c_buy'] - pos_info[index-1]['c_buy']
            tmp['c_sell_chg'] = tmp['c_sell'] - pos_info[index-1]['c_sell']
            tmp['f_buy_chg'] = tmp['f_buy'] - pos_info[index-1]['f_buy']
            tmp['f_sell_chg'] = tmp['f_sell'] - pos_info[index-1]['f_sell']
        else:
            tmp['c_buy_chg'] = 0
            tmp['c_sell_chg'] = 0
            tmp['f_buy_chg'] = 0
            tmp['f_sell_chg'] = 0
        tmp["c_chg"] =  tmp['c_buy_chg'] - tmp['c_sell_chg'] # ÂòÑ¹
        tmp["c_buy_per"] =  0 # ÂòÑ¹±È --TODO
        tmp["c_obs"] =  0 # ×èÁ¦ --TODO
        tmp["f_chg"] =  tmp['f_sell_chg'] - tmp['f_buy_chg'] # ÂôÑ¹
        tmp["up"] = 0
        tmp["down"] = 0
        #print tmp
        pos_info.append(tmp)
        index += 1
    return pos_info

def priceInfo ():
    price_dt = readFileLines(price_file)
    price_info =[]
    day = "2009.07.15"
    up = down = day_open =  day_close = 0
    day_high = high_cnt = low_cnt = for_i= 0
    day_low = 10000
    for one in price_dt:
        one = one.split(",")
        open_p = float(one[2])
        high_p = float(one[3])
        low_p = float(one[4])
        close_p = float(one[5])
        price_walk = close_p - open_p
        if one[0] == day:
            if price_walk > 0:
                up += price_walk
            else:
                down += abs(price_walk)
            if day_open == 0:
                day_open = open_p
            day_close = close_p
            
            if high_p > day_high:
                day_high = high_p
                high_cnt = for_i
            if low_p < day_low:
                day_low = low_p
                low_cnt = for_i
        else:
#            if price_walk > 0:
#                up += price_walk
#            else:
#                down += abs(price_walk)
            if day_low == 10000:
                day_low = 0
            if high_cnt >= low_cnt:
                up = day_high - day_low
                down = day_open - day_low + day_high - day_close
            else:
                up = day_high - day_open + day_close - day_low
                down = day_high - day_low
            price_info.append([ day, up, down, day_open, day_close ])
            day_open = open_p
            day_close = close_p
            high_cnt = low_cnt = day_high = 0
            day_low = 10000
#            print [ day, up, down, day_open, day_close ]
            if price_walk > 0:
                up = price_walk
                down = 0
            else:
                up = 0
                down = abs(price_walk)
#            up = down = 0
            day = one[0]
        for_i += 1
    price_info.append([ day, up, down ])
#    print [ day, up, down ]
    return price_info

def directionGuess(data, prev):
    if data['c_chg'] == 0:
        return 0
    price_p = 0
    
    if abs(data['c_chg_old']) > 17000:
        price_p = data['c_chg_old'] / abs(data['c_chg_old'])
        
#    if data['walk_old'] * prev['walk_old'] > 0 and abs(data['walk_old']) > 10:# and abs(prev['walk_old']) > 10:
#    if data['walk_old'] > 0:
#        price_p = data['walk_old'] / abs(data['walk_old'])
    
#    if data['c_chg'] * prev['c_chg'] > 0 and data['walk_per'] > prev['walk_per'] and prev['walk_per'] > 0:
#        if data['c_chg'] * data['c_chg_old'] > 0 and  data['c_chg_old'] * data['walk_per_old'] > 0:
#            price_p = data['c_chg'] / abs(data['c_chg'])
#        if data['c_chg'] * data['c_chg_old'] < 0 and  data['c_chg_old'] * data['walk_per_old'] < 0:
#            price_p = data['c_chg'] / abs(data['c_chg'])
            
#    direction = data['c_chg'] / abs(data['c_chg'])
#    if data['c_chg'] * data['c_chg_old'] > 0:
#        if data['walk_per'] > 0 and data['walk_per_old'] > 0 and data['walk_per_old'] > data['walk_per'] and abs(data['walk']) > 15 and abs(data['walk_old']) > 10 and abs(data['walk']) -  abs(data['walk_old']) > 10:
#            if direction > 0:
#                if data['walk'] > data['walk_old']:
#                    price_p = direction
#            else:
#                if data['walk'] < data['walk_old']:
#                    price_p = direction
#    elif data['c_chg'] * data['c_chg_old'] < 0:
#        if 
#    else:
#        price_p = 0
    return price_p
 

def longTime(week_cnt, pos_info):
    res = []
    pos_len = len(pos_info)
    for i in range(pos_len):
        cnt = week_cnt
        if i - week_cnt < 0:
            cnt = i+1
        tmp = {}
        tmp['c_chg'] = 0
        tmp['c_buy_chg'] = 0
        tmp['c_sell_chg'] = 0
        tmp['up'] = 0
        tmp['down'] = 0
        tmp['down_all'] = 0
        tmp['up_all'] = 0
        for j in range(cnt):
            index = i - (cnt - j) + 1
            if j == 0:
                tmp['open'] = pos_info[index]['open']    
            tmp['c_chg'] += pos_info[index]['c_chg']  
            tmp['c_buy_chg']  += pos_info[index]['c_buy_chg']  
            tmp['c_sell_chg']  += pos_info[index]['c_sell_chg']  
            tmp['up'] += pos_info[index]['up']  
            tmp['down'] += pos_info[index]['down']  
            tmp['up_all'] += pos_info[index]['up_all'] 
            tmp['down_all'] += pos_info[index]['down_all'] 
            
#            print index,
        tmp['close'] = pos_info[i]['close']
        tmp['date'] = pos_info[i]['date']
        tmp['walk_old'] = pos_info[i]['walk']
        tmp['c_chg_old'] = pos_info[i]['c_chg']
        tmp['c_buy_chg_old'] = pos_info[i]['c_buy_chg']
        tmp['c_sell_chg_old'] = pos_info[i]['c_sell_chg']
        tmp['walk_per_old'] = pos_info[i]['walk_per']
#        tmp['up'] = pos_info[i]['up']
#        tmp['down'] = pos_info[i]['down']
        tmp['walk'] = tmp['close'] - tmp['open']
        if tmp['c_chg'] != 0:
            tmp['walk_per'] = tmp['walk'] / tmp['c_chg'] * 10000 #* 5000
        else:
            tmp['walk_per'] = 0
        tmp['up_per'] = tmp['up'] / tmp['up_all'] * 10000 #* 5000
#        tmp['up_per'] = tmp['up_all'] / tmp['up']
        tmp['down_per'] = tmp['down'] / tmp['down_all'] * 10000 #* 5000
#        tmp['down_per'] = tmp['down_all'] / tmp['down']
        if abs(tmp['up_per']) > 500 or abs(tmp['down_per']) > 500:
            tmp['down_per'] = tmp['up_per'] = 0
            print tmp
        res.append(tmp)        
    return res

def mkRes(data):
    pos_price = []
    count_guess = 0
    previous = []
    for one in data:
        tmp = []
        tmp.append(one['date'])
        tmp.append((one['up_per'] + one['down_per'])/2)
        vol_avg = (one['up_all'] + one['down_all'])/2
        if vol_avg > 30000 * week_range:
            vol_avg = 30000 * week_range
        tmp.append(vol_avg/1000)
        tmp.append(one['c_chg']/1000)
        tmp.append(one['down'])
        tmp.append(one['walk_old'])
        tmp.append(one['close'] - one['open'])
        tmp.append(one['c_buy_chg_old'])
        tmp.append(one['c_chg_old'])
        tmp.append(one['walk_per'])
        tmp.append(one['walk_per_old'])
        guess = directionGuess(one, previous)
#                if guess != 0:
        tmp.append(guess)
        previous = one
#                if buy_per > sell_per:
#                    print 1
#                else:
#                    print -1
#                print one[0]
        if guess != 0:
#                if pos_info[index]['c_chg'] * (pos_info[index]['buy_per'] - pos_info[index]['sell_per']) < 0:
            count_guess += 1
#                    print tmp
#                print pos_info[index]
        pos_price.append(tmp)
#    print count_guess
    mkCsvFileWin(res_file, pos_price)
    print "done res file"
    
def main():
    pos_info = posInfo();
    pos_len = len(pos_info)
    price_info = priceInfo()
    index = 0
    pos_price = []
    lonely_price = [0, 0]
    open_p = close_p = 0
    count_guess = 0
    for one in price_info:
        if pos_len > index:
            if one[0] < pos_info[index]['date']:
                pos_info[index]['up'] += one[1]
                pos_info[index]['down'] += one[2]
                if open_p == 0:
                    open_p = one[3]
                try:
                    close_p = one[4]
                except:
                    print one, 1
                    exit(0)
#                print one
            else:
#                print one
                pos_info[index]['open'] = open_p
                pos_info[index]['close'] = close_p
                open_p = one[3]
                try:
                    close_p = one[4]
                except:
                    print one, 2
                    exit(0)
                up_all = down_all = 1
                if pos_info[index]['c_buy_chg'] > 0:
                    up_all += pos_info[index]['c_buy_chg']
                else:
                    down_all += abs(pos_info[index]['c_buy_chg'])
                if pos_info[index]['c_sell_chg'] > 0:
                    down_all += pos_info[index]['c_sell_chg']
                else:
                    up_all += abs(pos_info[index]['c_sell_chg'])
                if pos_info[index]['f_buy_chg'] > 0:
                    up_all += pos_info[index]['f_buy_chg']
                else:
                    down_all += abs(pos_info[index]['f_buy_chg'])
                if pos_info[index]['f_sell_chg'] > 0:
                    down_all += pos_info[index]['f_sell_chg']
                else:
                    up_all += abs(pos_info[index]['f_sell_chg'])
                pos_info[index]['up_all'] = up_all
                pos_info[index]['down_all'] = down_all
                buy_per = pos_info[index]['up'] / up_all * 10000
                sell_per = pos_info[index]['down'] / down_all * 10000
                if buy_per > 10000:
                    buy_per = -1
                if sell_per > 10000:
                    sell_per = -1
                pos_info[index]['buy_per'] = buy_per
                pos_info[index]['sell_per'] = sell_per
                pos_info[index]['walk'] = pos_info[index]['close'] - pos_info[index]['open']
                if pos_info[index]['c_chg'] != 0:
                    pos_info[index]['walk_per'] = pos_info[index]['walk'] / pos_info[index]['c_chg'] * 10000
                else:
                    pos_info[index]['walk_per'] = 0

                index += 1
                if pos_len > index:
                    pos_info[index]['up'] += one[1]
                    pos_info[index]['down'] += one[2]
                else:
                    lonely_price[0] += one[1]
                    lonely_price[1] += one[2]
        else:
            lonely_price[0] += one[1]
            lonely_price[1] += one[2]
#    print count_guess
    res = longTime(week_range, pos_info)
    mkRes(res)
    return

if __name__ == "__main__":
    main()
#   =IF(B2*E1>0,1,IF(E1=0,0,-1))
