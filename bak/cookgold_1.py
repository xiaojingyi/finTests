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

price_file = "data/XAUUSD30.csv"
pos_file = "data/position.csv"
per_range = 0.33

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
        #print tmp
        pos_info.append(tmp)
        index += 1
    return pos_info

def priceInfo ():
    price_dt = readFileLines(price_file)
    price_info =[]
    day = "2009.07.15"
    up = down = 0
    for one in price_dt:
        one = one.split(",")
        open_p = float(one[2])
        close_p = float(one[5])
        price_walk = close_p - open_p
        if one[0] == day:
            if price_walk > 0:
                up += price_walk
            else:
                down += abs(price_walk)
        else:
            price_info.append([ day, up, down ])
#            print [ day, up, down ]
            if price_walk > 0:
                up = price_walk
                down = 0
            else:
                up = 0
                down = abs(price_walk)
            day = one[0]
    price_info.append([ day, up, down ])
#    print [ day, up, down ]
    return price_info

def direction(per, avg):
    direction_future = 0
    if per < avg * per_range:
        direction_future = -1
    elif per >= avg:
        direction_future = 1
    return direction_future

def main():
    pos_info = posInfo();
    pos_len = len(pos_info)
    
    price_info = priceInfo()
    return
    price = []
    price_dt = readFileLines(price_file)
    index = 0
    open_p = 0
    pos_price = []
    for one in price_dt:
        one = one.split(",")
        day = one[0]
        if pos_len > index:
            if open_p == 0:
                open_p = float(one[2])
            if (day < pos_info[index]['date']):
                close_p = float(one[5])
                continue
            else:
                pos_info[index]['open'] = open_p
                pos_info[index]['close'] = close_p
                pos_info[index]['walk'] = close_p - open_p
                if pos_info[index]['c_chg'] != 0:
                    pos_info[index]['walk_per'] = pos_info[index]['walk'] / pos_info[index]['c_chg'] * 10000
                    if abs(pos_info[index]['walk_per']) > 100:
                        pos_info[index]['walk_per'] = 100 * pos_info[index]['walk_per'] / abs(pos_info[index]['walk_per'])
                    # the directions start
                    direction_crr = pos_info[index]['walk'] / abs(pos_info[index]['walk'])
                    if direction_crr > 0:
                        if pos_info[index]['c_chg'] > 0:
                            direction_future = direction(pos_info[index]['walk_per'], 10)
#                            if pos_info[index]['c_chg'] > 25000: #avg 9
#                                direction_future = direction(pos_info[index]['walk_per'], 9)
#                            elif pos_info[index]['c_chg'] > 15000: #avg 12
#                                direction_future = direction(pos_info[index]['walk_per'], 12)
#                            elif pos_info[index]['c_chg'] > 8000: #avg 16
#                                direction_future = direction(pos_info[index]['walk_per'], 16)
#                            elif pos_info[index]['c_chg'] > 4000: #avg 20
#                                direction_future = direction(pos_info[index]['walk_per'], 24)
#                            else: # avg 9
#                                direction_future = direction(pos_info[index]['walk_per'], 9)
                        if pos_info[index]['c_chg'] < 0:
                            direction_future = 1
                    if direction_crr < 0:
                        if pos_info[index]['c_chg'] > 0:
                            direction_future = 1
                        if pos_info[index]['c_chg'] < 0:
                            direction_future = direction(pos_info[index]['walk_per'], 10)
#                            if pos_info[index]['c_chg'] < -25000: #avg 10
#                                direction_future = direction(pos_info[index]['walk_per'], 10)
#                            elif pos_info[index]['c_chg'] < -15000: #avg 14
#                                direction_future = direction(pos_info[index]['walk_per'], 14)
#                            elif pos_info[index]['c_chg'] < -8000: #avg 15
#                                direction_future = direction(pos_info[index]['walk_per'], 15)
#                            elif pos_info[index]['c_chg'] < -4000: #avg 14
#                                direction_future = direction(pos_info[index]['walk_per'], 14)
#                            else: # avg 15
#                                direction_future = direction(pos_info[index]['walk_per'], 15)
                    pos_info[index]['direction'] = direction_future * direction_crr
                    if index > 1:
                        if pos_info[index-1]['direction'] != 0 and pos_info[index-1]['direction'] == direction_crr:
                            pos_info[index]['ok'] = 1
                        elif pos_info[index-1]['direction'] == 0:
                            pos_info[index]['ok'] = 0
                        else:
                            pos_info[index]['ok'] = -1
                    # the directions end
                    pos_price.append([pos_info[index]['date'], pos_info[index]['walk'], pos_info[index]['c_chg'], pos_info[index]['walk_per'], pos_info[index]['direction']])
                    print pos_info[index]['date'], pos_info[index]['walk'], pos_info[index]['c_chg'], pos_info[index]['walk_per']
                open_p = float(one[2])
                close_p = float(one[5])
                index += 1
        else:
            close_p = float(one[5])
    pos_price.append(['time ?', close_p - open_p])
    print close_p - open_p
    mkCsvFileWin("res.csv", pos_price)
    return

if __name__ == "__main__":
    main()
#   =IF(B2*E1>0,1,IF(E1=0,0,-1))
