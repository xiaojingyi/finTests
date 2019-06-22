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
import Order
import TrueOrder
import random

BIG_MODE_LEN = 3
DEBUG_PRINT = False

stop_lose = 35;
stop_win = 500;
stop_lose_true = 35;
stop_win_true = 300;
stop_chg_step=1;
global_point = 0.5 # 点差
global_price_chg_min = 1.2 # 最小变动
global_stop_g= 0.5;
global_give_opside = 1;
global_error_sum = 0;
global_deal_sum=0;
global_crr_direction=0;
global_crr_dcount=0;
global_lock_direction=0;
global_test_data = []
global_data_index = 0
global_true_order_direction = 1
test_result = []
test_print_index = 0
global_error_chg_per_max = 45
global_error_chg_per_min = 50
global_error_ls_len = 100
global_error_ls = []
global_error_index = 0
global_error_index_e_01 = 0
global_error_index_e_01_ls = []
global_error_index_e_01_avg = 0
global_error_index_e_01_avg_ls = [0]
global_true_stop_direction = 0

test_file = "data/XAUUSD60.csv"
res_file = "server_test_res.csv"
tmp_data = readFileLines(test_file)
for one in tmp_data:
    tmp_one = one.split(",")
    if tmp_one:
        global_test_data.append(tmp_one)

def mkMiniLine():
    global global_test_data, global_data_index, stop_lose, stop_win
    one = global_test_data[global_data_index]
    global_data_index += 1
#    print one
    # make mini data
    open_p = float(one[2])
    high_p = float(one[3])
    low_p = float(one[4])
    close_p = float(one[5])
    vol = float(one[6])
    price_walk = close_p - open_p
#    stop_lose = low_p

    if price_walk == 0:
        return
    price_percent = abs(price_walk) / (high_p - low_p)
    price_walk_e = price_walk * (price_percent ** 3)
#    if abs(price_percent) > 70:
#        return
#    print price_walk, ", ", price_walk * 100 / (high_p - low_p)
    
    
#    print price_walk
#    price_walk = price_walk / abs(price_walk)
#    price_walk *= high_p - low_p
    walk_per = price_walk / vol * 1000
    avg_price = close_p
#    avg_price = open_p # error price
    mini_line = [one[0], one[1], walk_per, price_walk, vol, avg_price, high_p, low_p, price_walk_e]
#    print [one[0], one[1], walk_per, price_walk, vol, avg_price]
    return mini_line

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

def newErrIndex(is_err, profit):
    global global_error_index, global_error_ls, global_error_ls_len, global_give_opside, global_error_chg_per_max, global_error_chg_per_min
    global global_error_index_e_01, global_error_index_e_01_avg, global_error_index_e_01_ls, global_error_index_e_01_avg_ls
    global global_true_order_direction, global_point
#    print profit, global_error_index
    a01 = 0.991
    global_error_index_e_01 = a01*global_error_index_e_01 + (1-a01) * is_err
    global_error_index += profit    
    global_error_index_e_01_ls.append(global_error_index)
    index_arr_len = len(global_error_index_e_01_ls)
    if index_arr_len >5:
        index_arr_len -= 1
        del global_error_index_e_01_ls[0]
        global_error_index_e_01_avg = 0
        for one in global_error_index_e_01_ls:
            global_error_index_e_01_avg += one / index_arr_len
        diff = global_error_index_e_01_avg - global_error_index_e_01_avg_ls[-1]
#        if diff < 0:
#            global_true_order_direction = -1
#        else:
#            global_true_order_direction = 1
#        if diff < -global_point*0.5:
#            global_true_order_direction = -1
#        elif diff > 0:
#            global_true_order_direction = 1
#        else:
#            global_true_order_direction = 0
#        print global_error_index_e_01_avg_ls[-1] < global_error_index_e_01_avg
        global_error_index_e_01_avg_ls.append(global_error_index_e_01_avg)
    return 

def sendOrder(sig, price, date_info, is_urgent, debug_info):    
    global stop_lose, stop_win, global_give_opside, global_price_chg_min, global_error_index
    global global_true_stop_direction
    
    order_info = {}
#    print sig, global_give_opside
#    print global_true_order_direction
    if sig == "0" or sig == False or global_give_opside == 0:
        return order_info
    if global_give_opside < 0:
        if sig == "1":
            sig = "2"
        elif sig == "2":
            sig = "1"
    
    if sig == "1":
        if Order.isDealOpen():
            if Order.global_deal["direction"] == Order.OP_SELL:
                order_profit = Order.orderProfit(Order.global_deal, price)
#                if (abs(order_profit) > global_price_chg_min and order_profit > 0) or order_profit <= 0:
                if abs(order_profit) > global_price_chg_min or is_urgent:
                    order_info = Order.orderClose(date_info, price, Order.STOP_T_CMD)
                    TrueOrder.orderClose(date_info, price, Order.STOP_T_CMD)
                    if order_info:
                        if order_profit < 0:
                            newErrIndex(1, order_info["profit"])
                        else:
                            newErrIndex(-1, order_info["profit"])
                if order_info:
                    1# none
                    testPrint([debug_info[0], debug_info[1], "close", order_info["profit"]>0, date_info, price, order_info["profit"], global_error_index, global_error_index_e_01_avg])
        order_info = Order.orderSend(date_info, Order.OP_UP, price, price-stop_lose, price+stop_win)
        if order_info and global_true_order_direction != 0:
            if global_true_order_direction > 0:
                if global_true_stop_direction != Order.OP_UP:
                    TrueOrder.orderSend(date_info, Order.OP_UP, price+global_point, price-stop_lose_true, price+stop_win_true)
                    global_true_stop_direction = 0
            else:
                if global_true_stop_direction != Order.OP_SELL:
                    TrueOrder.orderSend(date_info, Order.OP_SELL, price-global_point, price+stop_lose_true, price-stop_win_true)
                    global_true_stop_direction = 0
    elif sig == "2":
        if Order.isDealOpen():
            if Order.global_deal["direction"] == Order.OP_UP:
                order_profit = Order.orderProfit(Order.global_deal, price)
#                if (abs(order_profit) > global_price_chg_min and order_profit > 0) or order_profit <= 0:
                if abs(order_profit) > global_price_chg_min or is_urgent:
                    order_info = Order.orderClose(date_info, price, Order.STOP_T_CMD)
                    TrueOrder.orderClose(date_info, price, Order.STOP_T_CMD)
                    if order_info:
                        if order_profit < 0:
                            newErrIndex(1, order_info["profit"])
                        else:
                            newErrIndex(-1, order_info["profit"])
                if order_info:
                    1 # none
                    testPrint([debug_info[0], debug_info[1], "close", order_info["profit"]>0, date_info, price, order_info["profit"], global_error_index, global_error_index_e_01_avg])
        order_info = Order.orderSend(date_info, Order.OP_SELL, price, price+stop_lose, price-stop_win)
        if order_info and global_true_order_direction != 0:
            if global_true_order_direction > 0:
                if global_true_stop_direction != Order.OP_SELL:
                    TrueOrder.orderSend(date_info, Order.OP_SELL, price-global_point, price+stop_lose_true, price-stop_win_true)
                    global_true_stop_direction = 0
            else:
                if global_true_stop_direction != Order.OP_UP:
                    TrueOrder.orderSend(date_info, Order.OP_UP, price+global_point, price-stop_lose_true, price+stop_win_true)
                    global_true_stop_direction = 0
    elif sig =="3":
        order_profit = Order.orderProfit(Order.global_deal, price)
        if abs(order_profit) > global_price_chg_min or is_urgent:
            order_info = Order.orderClose(date_info, price, Order.STOP_T_CMD)
            TrueOrder.orderClose(date_info, price, Order.STOP_T_CMD)
            if order_info:
                if order_profit < 0:
                    newErrIndex(1, order_info["profit"])
                else:
                    newErrIndex(-1, order_info["profit"])
#    testPrint([debug_info[1], debug_info[2], debug_info[5], debug_info[6], debug_info[7], debug_info[8]])
#    testPrint(order_info)
    if order_info:
        if sig == "3":
            testPrint([debug_info[0], debug_info[1], "close", order_info["profit"]>0, date_info, price, order_info["profit"], global_error_index, global_error_index_e_01_avg])
        else:
            testPrint([debug_info[0], debug_info[1], sig, 0, date_info, price, order_info["profit"], global_error_index, global_error_index_e_01_avg])
    return order_info

def smoothIndex(crr_indexs, lst_indexs):
    for i in range(len(crr_indexs)):
        lst_indexs[i] = 0.2 * crr_indexs[i] + 0.8 * lst_indexs[i]
    return lst_indexs

def main():
    global test_result, global_test_data, global_data_index, global_error_index, global_give_opside
    global global_true_order_direction, global_true_stop_direction
    import Analyse_pool_todo as Analyse
    
    test_tmp = 0
    stop_direction = 0
    crr_direction = 0
    smooth_market_indexs = [0,0,0,0,0,0]
    zero_max = 3
    Analyse.initAnaType("time")
    Analyse.initPoolSize(18, "time")
    while(1):
        if global_data_index >= len(global_test_data):
            break
        one = mkMiniLine()
        if not one:
            continue
        
        check_info = Order.checkTick(one[6], one[7], one[5])
        if check_info:
            zero_max = 3
            stop_direction = global_give_opside * check_info['direction']
            testPrint(["0", "0", "stop", check_info["profit"]>0, one[0] + " " + one[1], one[5], check_info["profit"], 0, 0])
            global_error_index += check_info['profit']
#            testPrint(["stop", check_info["profit"]>0, one[0] + " " + one[1], one[5], 0, 0, 0, 0, 0, 0])
        check_info_true = TrueOrder.checkTick(one[6], one[7], one[5])
#        if check_info_true:
#            global_true_stop_direction = global_give_opside * check_info_true['direction']
#            print global_true_stop_direction
            
        Analyse.addData(one[:])
                
        res = Analyse.calcPool()
#        if res:
#            testPrint([one[0] + " " + one[1], one[5], one[5]+res[3]*10])
#        else:
#            testPrint([one[0] + " " + one[1], one[5], one[5]])

        if res:
            crr_sig = Analyse.crrSigStatus()
            testPrint(crr_sig)
            if crr_sig[0] == 0 and crr_sig[1] > zero_max:
                if Order.orderProfit(Order.global_deal, one[5])  < 0:
                    sendOrder("3", one[5], one[0] + " " + one[1], True, crr_sig)
                    stop_direction = global_give_opside * Order.global_deal['direction']
            if crr_sig[0] != 0 :
                zero_max = crr_sig[1] ** 2.7 * 5
#                print "sig: ", crr_sig, ", opside_flag: ", global_give_opside, "crr: ", crr_direction
#                if crr_direction != 0:
#                    if crr_sig[1] >= 30:
#                        global_true_order_direction = -1
#                    if crr_direction != crr_sig[0]:
#                        global_true_stop_direction = crr_sig[0]
#                        global_true_order_direction = 1
                crr_direction = crr_sig[0]
                
            opt = Analyse.addDeal(res)
            if opt:
                for one_opt in opt:
#                    one_opt = str(random.randint(1,2))
#                    print stop_direction
                    if stop_direction == Order.OP_SELL:
#                        print stop_direction, one_opt
                        if one_opt == "2":
                            one_opt = "3"
                        elif one_opt == "1":
                            stop_direction = 0
                    elif stop_direction == Order.OP_UP:
#                        print stop_direction, one_opt
                        if one_opt == "1":
                            one_opt = "3"
                        elif one_opt == "2":
                            stop_direction = 0
#                    print global_true_order_direction
#                    if one_opt == "2":
#                        one_opt = "3"
                    order_info = sendOrder(one_opt, one[5], one[0] + " " + one[1], False, crr_sig)
#            print res
#            testPrint(res)
    res = Order.profitInfo()
    res_real = TrueOrder.profitInfo()
    mkCsvFileWin("test_deals_info.csv", res)
    mkCsvFileWin("test_deals_info_real.csv", res_real)
    mkCsvFileWin("test_info.csv", test_result)
    print test_tmp
    print "done res file"

if __name__ == "__main__":
    main()
    