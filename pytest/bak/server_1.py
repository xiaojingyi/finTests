#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2013-8-16 14:41:13$
# Note: This source file is NOT a freeware
# Version: cook_std.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2014-12-20 21:17:02$"
import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

from math import *
from lib.Util import *
import time

sleep_set = 0.01
vol_size = 100
time_len = 1
g = 1
diff = 0.7
stop_lose = -3
stop_win = 30
stop_len = 5
crr_deals = []
deals_len = 10000
deals_err_max = 6000
give_opside = 0

if give_opside == 1:
    tmp = stop_win
    stop_win = -stop_lose
    stop_lose = -tmp

fcmd = "C:/Users/jingyi/AppData/Roaming/MetaQuotes/Terminal/B2354B081A56707F0514B028C79E9419/tester/files/cmd.csv"
fdata = "C:/Users/jingyi/AppData/Roaming/MetaQuotes/Terminal/B2354B081A56707F0514B028C79E9419/tester/files/data.csv"

def mkMiniLine():
    data = ""
    while (1):
        data = getFileContent(fdata)
        if not data:
            time.sleep(0.1)
            continue
        else:
            break
    one = data.split(",")
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
    return mini_line

opt_ct = 0
def sendOrder(sig):
    global opt_ct
    if give_opside:
        if sig == "1":
            sig = "2"
        elif sig == "2":
            sig = "1"
            
    is_stop = 0
    while(1):
        try:
#            print "in send"
            writeToFile(fcmd, sig)
#            print "after send"
            opt_ct += 1
            print opt_ct, sig
            if sig == "3":
                time.sleep(1)
            is_stop = 1
#            print is_stop
        except:
#            print "send sig loop: ", sig
            time.sleep(0.2)
#            print is_stop
        if is_stop == 1:
            break
    return

def main():
    mini_line = []
    vol_sum = per = price_vol = 0
    per_ls = []
    price_info = []
    index = prev_index = prev_price = 0
    one_deal = []
    while(1):
        one = mkMiniLine()
        if not one:
            continue
        
        if one and mini_line and mini_line[0] == one[0]:
            time.sleep(sleep_set)
            continue
            
        mini_line = one
        if prev_price == 0:
            prev_price = mini_line[5]
            
#        print mini_line
        # make big data start ------------------------------------
        if vol_sum < vol_size:
            per_ls.append([mini_line[2], mini_line[4]])
            vol_sum += mini_line[4]
            price_vol += mini_line[5] * mini_line[4]
#            print mini_line[0], vol_sum
        else:
#            print mini_line[0], vol_sum
            for per_one in per_ls:
                per += per_one[0] * per_one[1] / vol_sum
            price_line = [mini_line[0], mini_line[1], per, mini_line[3], vol_sum, price_vol / vol_sum]
            print price_line
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
            # calc start ------------------------------------
            index = ana_line[2]
            # calc 1 start ------------------------------------------------------------------------------------------------------------
#            if index > 0:
#                if prev_index > 0 and prev_index < index:
#                    if len(one_deal) > 0: # have deal
#                        if one_deal[0] == 1: # buy deal clean
#                            one_deal = []
#                            sendOrder("3")
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [-1, ana_line[3], 0, index, 0, 1]
#                        sendOrder("2")
#                if prev_index < 0:
#                    if len(one_deal) > 0:
#                        if one_deal[0] == -1:
#                            one_deal = []
#                            sendOrder("3")
#            elif index < 0:
#                if prev_index < 0 and prev_index > index:
#                    if len(one_deal) > 0: # have deal
#                        if one_deal[0] == -1: # sell deal clean
#                            one_deal = []
#                            sendOrder("3")
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [1, ana_line[3], 0, index, 0, 1]
#                        sendOrder("1")
#                if prev_index > 0:
#                    if len(one_deal) > 0:
#                        if one_deal[0] == 1:
#                            one_deal = []
#                            sendOrder("3")
            # calc 1 end ------------------------------------------------------------------------------------------------------------
            # calc 2 start ------------------------------------------------------------------------------------------------------------
#            if index> 0:
#                if index - g > 0 and prev_index > 0 and prev_index < index:
##                if prev_index > 0:
#                    if len(one_deal) > 0: # have deal
#                        if one_deal[0] == -1: # sell deal clean
#                            writeToFile(fcmd, "3")
#                            one_deal = []
#                            time.sleep(1)
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [1, ana_line[3], 0, index, 0, 1]
#                        writeToFile(fcmd, "1")
#                if prev_index + g < 0:
#                    if len(one_deal) > 0:
#                        if one_deal[0] == 1:
#                            writeToFile(fcmd, "3")
#                            one_deal = []
#            elif index < 0:
#                if index + g < 0 and prev_index < 0 and prev_index > index:
##                if prev_index < 0:
#                    if len(one_deal) > 0: # have deal
#                        if one_deal[0] == 1: # buy deal clean
#                            writeToFile(fcmd, "3")
#                            one_deal = []
#                            time.sleep(1)
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [-1, ana_line[3], 0, index, 0, 1]
#                        writeToFile(fcmd, "2")
#                if prev_index - g > 0:
#                    if len(one_deal) > 0:
#                        if one_deal[0] == -1:
#                            writeToFile(fcmd, "3")
#                            one_deal = []
            # calc 2 end ------------------------------------------------------------------------------------------------------------
            # calc 3 start ------------------------------------------------------------------------------------------------------------
#            if index > 0:
#                if len(one_deal) > 0: # have deal
#                    if one_deal[0] == 1: # sell deal clean
#                        one_deal = []
#                        sendOrder("3")
#                if index - g > 0:
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [-1, ana_line[3], 0, index, 0, 1]
#                        sendOrder("2")
#            elif index < 0:
#                if len(one_deal) > 0: # have deal
#                    if one_deal[0] == -1: # buy deal clean
#                        one_deal = []
#                        sendOrder("3")
#                if index + g < 0:
#                    # direction price, out_price, index, err_ct, index_ct
#                    if len(one_deal) == 0:
#                        one_deal = [1, ana_line[3], 0, index, 0, 1]
#                        sendOrder("1")
            # calc 3 end ------------------------------------------------------------------------------------------------------------
            # calc 2 start ------------------------------------------------------------------------------------------------------------
            if index - prev_index > 0:
                if ana_line[3] - prev_price < 0:
                    if len(one_deal) > 0:
                        if one_deal[0] == -1:
                            sendOrder("3")
                            one_deal = []
                    if len(one_deal) == 0:
                        one_deal = [1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1], 0]
                        sendOrder("1")
            elif index - prev_index < 0:
                if ana_line[3] - prev_price > 0: # up
                    if len(one_deal) > 0:
                        if one_deal[0] == 1:
                            sendOrder("3")
                            one_deal = []
                    if len(one_deal) == 0:
                        one_deal = [-1, mini_line[5], 0, index, 0, 1, mini_line[0], mini_line[1], 0]
                        sendOrder("2")
            # calc 2 end ------------------------------------------------------------------------------------------------------------
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
            if len(one_deal) > 0 and one_deal[8] < stop_len:
                one_deal[8] += 1
            elif len(one_deal) > 0 and one_deal[8] >= stop_len:
                sendOrder("3")
                one_deal = []
        # stop lose start
            
        if len(one_deal):
            if one_deal[0] == 1:
                if one[7] - one_deal[1] - diff < stop_lose:
                    sendOrder("3")
                    one_deal = []
            elif one_deal[0] == -1:
                if one_deal[1] - diff - one[6] < stop_lose:
                    sendOrder("3")
                    one_deal = []
        # stop lose end
        time.sleep(sleep_set)
    print "done res file"
    
if __name__ == "__main__":
    main()