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
vol_size = 1000
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

def main():
    global one_deal, order_result, win_ct, opt_ct, amount_all
    mini_line = []
    vol_sum = per = price_vol = 0
    per_ls_up = []
    per_ls_down = []
    price_info = []
    index = prev_index = prev_price = price = 0
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
        if vol_sum < vol_size:
            
            per_ls.append([mini_line[2], mini_line[4]])
            vol_sum += mini_line[4]
            price_vol += price * mini_line[4]
#            print mini_line[0], mini_line[1], vol_sum
        else:
#            print mini_line[0], vol_sum
            for per_one in per_ls:
                per += per_one[0] * per_one[1] / vol_sum
            price_line = [mini_line[0], mini_line[1], per, mini_line[3], vol_sum, price_vol / vol_sum]
#            print price_line
            price_info.append(price_line)
            # price analyse start ------------------------------------
            price_len = len(price_info)
            up_ls = []
            down_ls = []
            i = price_len - 1
            for j in range(time_len):
                if price_len - j >= 0:
                    walk_per = float(price_info[i-j][2])
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
            ana_line = [price_line[0], price_line[1], (up_avg - down_avg), price_line[5]]
#            print ana_line
            # calc start ------------------------------------
            index = ana_line[2]
            # calc 1 start ------------------------------------------------------------------------------------------------------------
#            if index > 0:
#                if prev_index > 0 and prev_index < index:
#                    if len(one_deal) > 0: # have deal
#                        if one_deal[0] == 1: # buy deal clean
#                            sendOrder("3", mini_line[5])
#                    # direction, price, out_price, index, err_ct, index_ct, date, time
#                    if len(one_deal) == 0:
#                        one_deal = [-1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1]]
#                        sendOrder("2", mini_line[5])
#                if prev_index < 0:
#                    if len(one_deal) > 0:
#                        if one_deal[0] == -1:
#                            sendOrder("3", mini_line[5])
#            elif index < 0:
#                if prev_index < 0 and prev_index > index:
#                    if len(one_deal) > 0: # have deal
#                        if one_deal[0] == -1: # sell deal clean
#                            sendOrder("3", mini_line[5])
#                    if len(one_deal) == 0:
#                        # direction price, out_price, index, err_ct, index_ct, date, time
#                        one_deal = [1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1]]
#                        sendOrder("1", mini_line[5])
#                if prev_index > 0:
#                    if len(one_deal) > 0:
#                        if one_deal[0] == 1:
#                            sendOrder("3", mini_line[5])
            # calc 1 end ------------------------------------------------------------------------------------------------------------
            # calc 2 start ------------------------------------------------------------------------------------------------------------
            if index - prev_index > 0:
                if ana_line[3] - prev_price < 0:
                    if len(one_deal) > 0:
                        if one_deal[0] == 1:
                            sendOrder("3", mini_line[5])
                    if len(one_deal) == 0:
                        one_deal = [-1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1]]
                        sendOrder("2", mini_line[5])
            elif index - prev_index == 0:
                1 # none happen
#                if ana_line[3] - prev_price > 0: #up
#                    if len(one_deal) > 0:
#                        if one_deal[0] == -1:
#                            sendOrder("3", mini_line[5])
#                    if len(one_deal) == 0:
#                        one_deal = [1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1]]
#                        sendOrder("1", mini_line[5])
#                elif ana_line[3] - prev_price == 0:
#                    1 # none happen
#                else: # down
#                    if len(one_deal) > 0:
#                        if one_deal[0] == 1:
#                            sendOrder("3", mini_line[5])
#                    if len(one_deal) == 0:
#                        one_deal = [-1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1]]
#                        sendOrder("2", mini_line[5])
            elif index - prev_index < 0:
                if ana_line[3] - prev_price > 0: # up
                    if len(one_deal) > 0:
                        if one_deal[0] == -1:
                            sendOrder("3", mini_line[5])
                    if len(one_deal) == 0:
                        one_deal = [1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1]]
                        sendOrder("1", mini_line[5])
            # calc 2 end ------------------------------------------------------------------------------------------------------------
            # calc 3 start ------------------------------------------------------------------------------------------------------------
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
            # calc 3 end ------------------------------------------------------------------------------------------------------------
            prev_index = index
            prev_price = ana_line[3]
            # calc end ------------------------------------
            # price analyse end ------------------------------------
            #init
            per_ls = []
            per = vol_sum = price_vol = 0
            per_ls.append([mini_line[2], mini_line[4]])
            vol_sum += mini_line[4]
            price_vol += mini_line[5] * mini_line[4]
        # make big data end ------------------------------------
        # stop lose start
        if len(one_deal):
            if one_deal[0] == 1:
                if one[7] - one_deal[1] - diff < stop_lose:
                    sendOrder("3", mini_line[5])
            elif one_deal[0] == -1:
                if one_deal[1] - diff - one[6] < stop_lose:
                    sendOrder("3", mini_line[5])
        # stop lose end
#        time.sleep(sleep_set)
    mkCsvFileWin(res_file, order_result)
    print "winper, lose: ", win_ct * 100 / opt_ct, opt_ct
    print "all: ", amount_all
    print "done res file"
    
if __name__ == "__main__":
    main()
    