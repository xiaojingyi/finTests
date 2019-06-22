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
from ClassOrder import *
import random

BIG_MODE_LEN = 3
DEBUG_PRINT = False

stop_lose = 1000;
stop_win = 2000;
global_point = 0.5 # 点差
global_price_chg_min = 0 # 最小变动
global_give_opside = 1;
test_result = []
test_print_index = 0

global_order = Order(True, stop_lose)

global_source_file = "data/XAUUSD1-hst-new.csv"
#global_source_file = "data/XAUUSD1.csv"
#global_source_file = "data/XAUUSD5.csv"
#global_source_file = "data/tick_IF_all.csv"
#global_source_file = "data/tick_IF/20150311_IF.csv"
res_file = "server_test_res.csv"

def testPrint(dt):
    global test_result, test_print_index
    
    if not dt:
        return False
    
    if isinstance(dt, dict):
        data = dt.copy()
        tmp = []
        for k in data.keys():
            tmp.append(k)
            tmp.append(data[k])
        data = tmp
    else:
        data = dt[:]
        
    data.insert(0, test_print_index)
    test_print_index += 1
    if DEBUG_PRINT:
        print data
    test_result.append(data)
    return True

def sendOrder(sig, price, date_info, is_urgent, debug_info):    
    global stop_lose, stop_win, global_give_opside, global_price_chg_min
    global global_order
    
    order_info = {}
#    print sig, global_give_opside
    if sig == "0" or sig == False or global_give_opside == 0:
        return order_info
    if global_give_opside < 0:
        if sig == "1":
            sig = "2"
        elif sig == "2":
            sig = "1"
    
    if sig == "1":
        if global_order.dealOpen():
            if global_order.deal["direction"] == OP_SELL:
                order_profit = global_order.profit(global_order.deal, price)
#                if (abs(order_profit) > global_price_chg_min and order_profit > 0) or order_profit <= 0:
                if abs(order_profit) > global_price_chg_min or is_urgent:
                    order_info = global_order.close(date_info, price, STOP_T_CMD)
                if order_info:
                    1# none
        if not order_info or order_info['profit'] < 0:
            order_info = global_order.open(date_info, OP_UP, price, price-stop_lose, price+stop_win)
            
    elif sig == "2":
        if global_order.dealOpen():
            if global_order.deal["direction"] == OP_UP:
                order_profit = global_order.profit(global_order.deal, price)
#                if (abs(order_profit) > global_price_chg_min and order_profit > 0) or order_profit <= 0:
                if abs(order_profit) > global_price_chg_min or is_urgent:
                    order_info = global_order.close(date_info, price, STOP_T_CMD)
                if order_info:
                    1 # none
        if not order_info or order_info['profit'] < 0:
            order_info = global_order.open(date_info, OP_SELL, price, price+stop_lose, price-stop_win)
            
    elif sig =="3":
        order_profit = global_order.profit(global_order.deal, price)
        if abs(order_profit) > global_price_chg_min or is_urgent:
            order_info = global_order.close(date_info, price, STOP_T_CMD)
    return order_info

def smoothIndex(crr_indexs, lst_indexs):
    for i in range(len(crr_indexs)):
        lst_indexs[i] = 0.2 * crr_indexs[i] + 0.8 * lst_indexs[i]
    return lst_indexs

def main():
    global test_result, global_give_opside
    global stop_win, stop_lose
    import Analyse_price_walk as Analyse
    import DataSrc
    from ClassLine import Line
    import Market
    
    test_tmp = 0
    stop_direction = 0

    if global_source_file.find("IF") > 0:
        DataSrc.init(global_source_file, "IF")
    else:
        DataSrc.init(global_source_file, "MT4")
    
    i = 0
    signar = 0
    tmp_count = 0
    crr_price = 0
    price_walk = Line(Market.E_N_AVG, 3)
    price_ct_diff = Line(Market.E_N_AVG)
    shoot_diff = Line(Market.E_N_AVG)
    vol_ct_diff = Line(Market.E_N_AVG)
    vol_strong_win_diff = Line(Market.E_N_AVG)
    vol_weak_win_diff = Line(Market.E_N_AVG)
    vol_strong_lose_diff = Line(Market.E_N_AVG)
    vol_weak_lose_diff = Line(Market.E_N_AVG)
    vol_index_diff = Line(Market.E_N_AVG)
    vol_avg_diff = Line(Market.E_N_AVG)
    score = Line(20, 10)
    while(1):
        one = DataSrc.getLine()
#        if i < 120000:
#            i += 1
#            continue
#        if i > 170000:
#            break
#        print "line: ", one
        if not one:
            break
        crr_price = one[5]
        market = Market.listen(one)
        
        check_info = global_order.tick(one[6], one[7], one[5])
        if check_info:
            sendOrder("3", one[5], one[0] + " " + one[1], True, "")
#            if check_info['profit']< 0:
#                stop_direction = global_give_opside * check_info['direction']

        tmpw = market["info"]["price_crr_walk"]
        tmp1 = price_ct_diff.add(market["info"]["price_up_ct"] - market["info"]["price_sell_ct"])
        price_walk.add(market["info"]["price_crr_walk"])
        tmp2 = int(abs(tmpw) > 1)
#        print price_walk.point
        tmp = int(tmpw * tmp1 > 0) * tmp2

        
        tmpv1 = shoot_diff.add(market["info"]["vol_up_shoot"] - market["info"]["vol_sell_shoot"])
#        print shoot_diff.info()
#        print tmpv1
        tmpv2 = vol_ct_diff.add(market["info"]["vol_up_ct"] - market["info"]["vol_sell_ct"])
        tmpv3 = vol_strong_win_diff.add(market["info"]["vol_up_strong_win"] - market["info"]["vol_sell_strong_win"])
        tmpv4 = vol_weak_win_diff.add(market["info"]["vol_up_weak_win"] - market["info"]["vol_sell_weak_win"])
        tmpv5 = vol_strong_lose_diff.add(market["info"]["vol_up_strong_lose"] - market["info"]["vol_sell_strong_lose"])
        tmpv6 = vol_weak_lose_diff.add(market["info"]["vol_up_weak_lose"] - market["info"]["vol_sell_weak_lose"])
        tmpv71 = market["info"]["vol_up_weak_win"] + market["info"]["vol_up_weak_lose"] + market["info"]["vol_up_strong_win"] + market["info"]["vol_up_strong_lose"]
        tmpv72 = market["info"]["vol_sell_weak_win"] + market["info"]["vol_sell_weak_lose"] + market["info"]["vol_sell_strong_win"] + market["info"]["vol_sell_strong_lose"]
        tmpv7 = vol_index_diff.add(tmpv71 -  tmpv72)
        tmpv8 = vol_avg_diff.add(market["info"]["vol_avg_diff"])
        tmpv9 = market["info"]["vol_diff"] 
        tmpv = int(tmpv1 * tmpv2 > 0) * int(tmpv1 * tmpv3 > 0) * int(tmpv1 * tmpv6 > 0) * int(tmpv1 * tmpv7 > 0) * int(tmpv1 * tmpv8 > 0) * int(tmpv1 * tmpv4 > 0) * int(tmpv1 * tmpv5 > 0) #* int(tmpv1 * tmpv9 > 0)
        
        signar = tmpv1 * tmp * tmpv * int(tmpv1 * tmpw > 0)
#        score_sum = price_ct_diff.walk_score + shoot_diff.walk_score + vol_ct_diff.walk_score
#        score_sum = vol_strong_win_diff.walk_score + vol_weak_win_diff.walk_score + vol_strong_lose_diff.walk_score + vol_weak_lose_diff.walk_score + vol_index_diff.walk_score + vol_avg_diff.walk_score
#        signar = score.add(score_sum) * int(tmpw * score.last_n > 0)
        
#        signar = tmpv8
#        signar = random.randint(-1,1)
        if signar > 0:
            one_opt = "1"
        elif signar < 0:
            one_opt = "2"
        else:
            one_opt = "0"
                
#        if tmp9 == 0:
#            one_opt = "3"
            
        if stop_direction == OP_SELL:
            if one_opt == "2":
                one_opt = "3"
#            elif one_opt == "1":
            stop_direction = 0
        elif stop_direction == OP_UP:
            if one_opt == "1":
                one_opt = "3"
#            elif one_opt == "2":
            stop_direction = 0
        
        order_info = sendOrder(one_opt, one[5], one[0] + " " + one[1], False, "")
        i += 1
        if i % 1440 == 0:
            print i, one[0] + " " + one[1]
            if global_order.dealOpen():
                print global_order.deal["direction"], " deal(", signar, "): ", global_order.profit(global_order.deal, crr_price)
            else:
                print "no deal(", signar, ")"
            global_order.info()
            print "---------------------"

    DataSrc.done()
    res = global_order.info()
    order_info = sendOrder("3", crr_price, "last", True, "")
    if res:
        mkCsvFileWin("test_deals_info.csv", res)
    mkCsvFileWin("test_info.csv", test_result)
    print test_tmp
    print "done res file"

if __name__ == "__main__":
    main()
    