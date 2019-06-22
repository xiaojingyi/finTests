#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-3-19 21:04:03$
# Note: This source file is NOT a freeware
# Version: Order.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-3-19 21:04:03$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

from math import *
from lib.Util import *
import time

OP_UP = 1 # buy action
OP_SELL = -1 # sell action
STOP_T_LOSE = 1 # buy stop lose
STOP_T_WIN = 2 # buy stop win
STOP_T_CMD = 3 # buy cmd
STOP_CHG_MIN = 1

global_deal_history = []
global_deal_count = 0
global_deal_result = []
global_deal_win_count = 0
global_profit_sum = 0
global_deal_up_win = 0
global_deal_up_lose = 0
global_deal_sell_win = 0
global_deal_sell_lose = 0
global_deal_lose_max = global_deal_win_max = 0
global_deal_lose_avg = global_deal_win_avg = 0
global_deal_tick_sum = 0
global_deal = {
    "open_time": "",
    "close_time": "",
    "open_price": 0,
    "high_price": 0,
    "high_tick": 0,
    "low_price": 100000,
    "low_tick": 0,
    "tick": 0,
    "close_price": 0,
    "direction": 0,
    "profit": 0,
    "stop_lose": 0,
    "stop_win": 0,
    "stop_type": 0,
    "is_open": False
}

def profitInfo():
    global global_deal_result, global_deal_history
    global global_deal_lose_max, global_deal_win_max
    global global_deal_lose_avg, global_deal_win_avg
    if not global_deal_count:
        print "no deals"
        return
    print "winper: ", global_deal_win_count * 100.0 / global_deal_count
    print "total: ", global_deal_count
    print "detail: ", global_deal_up_win, global_deal_up_lose, global_deal_sell_win, global_deal_sell_lose
    print "profit: ", global_profit_sum
    print "win_max: ", global_deal_win_max
    print "lose_max: ", global_deal_lose_max
    print "win_avg: ", global_deal_win_avg
    print "lose_avg: ", global_deal_lose_avg
    print "tick_avg", global_deal_tick_sum / len(global_deal_history)
    return global_deal_result

def checkTick(high_p, low_p, crr_p, stop_lose):
    global OP_UP, OP_SELL
    global STOP_T_LOSE, STOP_T_WIN, STOP_CHG_MIN
    global global_deal
    ret = {}
    profit = 0
    if global_deal["is_open"] == True:
        global_deal["tick"] += 1
        if global_deal['high_price'] < crr_p:
            global_deal['high_price'] = crr_p
            global_deal['high_tick'] = global_deal["tick"]
        if global_deal['low_price'] > crr_p:
            global_deal['low_price'] = crr_p
            global_deal['low_tick'] = global_deal["tick"]
        profit = orderProfit(global_deal, crr_p)
        if global_deal['direction'] == OP_UP:
            if global_deal["stop_lose"] != 0 and global_deal["stop_lose"] > low_p: # who first? --TODO
                ret = orderClose("", global_deal["stop_lose"], STOP_T_LOSE)
#                print "stop lose reach: ", high_p, low_p, crr_p, global_deal
            if global_deal["stop_win"] != 0 and global_deal["stop_win"] < high_p:
                ret = orderClose("", global_deal["stop_win"], STOP_T_WIN)
#                print "stop win reach: ", high_p, low_p, crr_p, global_deal
        elif global_deal['direction'] == OP_SELL:
            if global_deal["stop_lose"] != 0 and global_deal["stop_lose"] < high_p: # who first? --TODO
                ret = orderClose("", global_deal["stop_lose"], STOP_T_LOSE)
#                print "stop lose reach: ", high_p, low_p, crr_p, global_deal
            if global_deal["stop_win"] != 0 and global_deal["stop_win"] > low_p:
                ret = orderClose("", global_deal["stop_win"], STOP_T_WIN)
#                print "stop win reach: ", high_p, low_p, crr_p, global_deal
#        print crr_p, global_deal['open_price'], global_deal['stop_lose'], global_deal['direction']
#        print profit
        if stop_lose > 0 and not ret and profit > STOP_CHG_MIN and (crr_p - global_deal["stop_lose"])* global_deal['direction'] > stop_lose :
#            print "before: ", global_deal['direction'], global_deal['stop_lose']
            global_deal["stop_lose"] = crr_p - stop_lose * global_deal['direction']
#            print "after: ", global_deal['direction'], global_deal['stop_lose']
#            print "-------------------------------------------", crr_p
    return ret

def isDealOpen():
    global global_deal
    if global_deal["is_open"] == True:
        return True
    return False

def orderProfit(deal, price):
    if deal:
        return (price - deal["open_price"]) * deal["direction"]
    return 0

def orderClose(tm, price, t):
    global OP_UP, OP_SELL
    global global_deal, global_deal_history, global_deal_win_count, global_deal_count, global_profit_sum
    global global_deal_up_win, global_deal_up_lose, global_deal_sell_win, global_deal_sell_lose
    global global_deal_lose_max, global_deal_win_max
    global global_deal_lose_avg, global_deal_win_avg
    global global_deal_tick_sum
    
    if global_deal["is_open"] == False:
        # already close
        return False
    profit = orderProfit(global_deal, price)
    global_deal["close_time"] = tm
    global_deal["close_price"] = price
    global_deal["is_open"] = False
    global_deal["stop_type"] = t
    global_deal["profit"] = profit
    global_deal_count += 1
    global_profit_sum += profit
    global_deal_tick_sum += global_deal["tick"]
    if profit < global_deal_lose_max:
        global_deal_lose_max = profit
    if profit > global_deal_win_max:
        global_deal_win_max = profit
    global_deal_history.append(global_deal.copy())
    if profit > 0:
        global_deal_win_avg = (global_deal_win_avg * global_deal_win_count + profit) / (global_deal_win_count+1)
        global_deal_win_count += 1
        if global_deal['direction'] == OP_UP:
            global_deal_up_win += 1
        elif global_deal['direction'] == OP_SELL:
            global_deal_sell_win += 1
    elif profit < 0:
        global_deal_lose_avg = (global_deal_lose_avg * (global_deal_up_lose+global_deal_sell_lose) + profit) / (global_deal_up_lose+global_deal_sell_lose+1)
        if global_deal['direction'] == OP_UP:
            global_deal_up_lose += 1
        elif global_deal['direction'] == OP_SELL:
            global_deal_sell_lose += 1
    #    print "order close: ", global_deal, profit
    global_deal_result.append([
        global_deal['open_time'], global_deal['open_price'], global_deal['high_price'], global_deal['low_price'], 
        int((global_deal["high_tick"] - global_deal['low_tick']) * global_deal['direction'] < 0), 
        global_deal["tick"], global_deal['direction'], profit, global_profit_sum 
        ])
    return global_deal.copy()

def orderSend(tm, opt, price, stop_lose, stop_win):
    global global_deal
    if global_deal["is_open"] == True:
        # already open
        return False
    
    global_deal["open_time"] = tm
    global_deal["close_time"] = 0
    global_deal["direction"] = opt
    global_deal['open_price'] = price
    global_deal["stop_lose"] = stop_lose
    global_deal["stop_win"] = stop_win
    global_deal["stop_type"] = 0
    global_deal["close_price"] = 0
    global_deal["profit"] = 0
    global_deal["is_open"] = True
    global_deal["tick"] = 1
    global_deal['high_price'] = global_deal['low_price'] = price
    global_deal['high_tick'] = global_deal['low_tick'] = 1
#    print "order open: ", global_deal
    return global_deal.copy()

if __name__ == "__main__":
    print "Hello World";
