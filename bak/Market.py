#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-2 18:24:00$
# Note: This source file is NOT a freeware
# Version: Market.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-2 18:24:00$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

E_N = 10
E_N_AVG = 1000
E_N_DEC = E_N_AVG

g_market_info = {
    # base_info
    "dt": "",
    # price info
    "price_o": 0,#
    "price_h": 0,#
    "price_l": 10000,#
    "price_c": 0,#
    "price_up_ct": 0,#
    "price_sell_ct": 0,#
    "price_crr_walk": 0,#
    "price_per": 0,#
    "price_walk": 0,#
    "price_walk_per": 0,#
    # walk info
    "walk_up": 0,#
    "walk_sell": 0,#
    "walk_diff": 0,# TODO no use
    "walk_up_avg": 0,#
    "walk_sell_avg": 0,#
    "walk_avg_diff": 0,#
    "walk_all": 0,#
    # vol info
    "vol_up": 0,#
    "vol_sell": 0,#
    "vol_diff": 0,#
    "vol_up_avg": 0,#
    "vol_up_ct": 0,
    "vol_up_shoot": 0,
    "vol_up_strong_win": 0,# strong win
    "vol_up_strong_lose": 0,# strong lose
    "vol_up_weak_win": 0,#weak_win
    "vol_up_weak_lose": 0,#weak_lose
    "vol_sell_avg": 0,#
    "vol_sell_ct": 0,
    "vol_sell_shoot": 0,
    "vol_sell_strong_win": 0,
    "vol_sell_strong_lose": 0,
    "vol_sell_weak_win": 0,
    "vol_sell_weak_lose": 0,
    "vol_avg_diff": 0,#
    "vol_all": 0,#
    # per info
    "per_all": 0,#
    "per_up": 0,#
    "per_sell": 0,#
    "per_upsell": 0,#
}
g_market_info_prev = g_market_info.copy()
g_market_info_diff = g_market_info.copy()
g_market_info_e = g_market_info.copy()
g_market_info_e_prev = g_market_info.copy()
g_market_info_e_diff = g_market_info.copy()
g_price_info_prev = []

def mkElseInfo():
    global g_market_info, g_market_info_prev, g_market_info_diff
    global g_market_info_e, g_market_info_e_prev, g_market_info_e_diff
    global E_N
    
    g_market_info_diff = diffMarket(g_market_info_prev, g_market_info)
    g_market_info_prev = g_market_info.copy()
    
    for k in g_market_info.keys():
        if k == "dt":
            g_market_info_e[k] = g_market_info[k]
        else:
            g_market_info_e[k] = E(g_market_info_e[k], g_market_info[k], E_N)
    
    g_market_info_e_diff = diffMarket(g_market_info_e_prev, g_market_info_e)
    g_market_info_e_prev = g_market_info_e.copy()
    return

def mkPriceInfo(price_info):
    global g_market_info
    
    decreaseIndex([
        "price_up_ct",
        "price_sell_ct",
    ])
    g_market_info["dt"] = price_info[0] + " " + price_info[1]
    if g_market_info["price_o"] == 0:
        g_market_info["price_o"] = price_info[9]
    g_market_info["price_c"] = price_info[5]
    if price_info[6] > g_market_info["price_h"]:
        g_market_info["price_h"] = price_info[6]
    elif price_info[7] < g_market_info["price_l"]:
        g_market_info["price_l"] = price_info[7]
    
    g_market_info["price_crr_walk"] = price_info[3]
    if price_info[3] > 0:
        g_market_info['price_up_ct'] += 1
    elif price_info[3] < 0:
        g_market_info['price_sell_ct'] += 1
        
    g_market_info["price_walk"] = g_market_info["price_c"] - g_market_info["price_o"]
    g_market_info["price_per"] = g_market_info["price_walk"] * 100.0 / (g_market_info["price_h"] - g_market_info["price_l"])
    return

def mkWalkInfo():
    global g_market_info
    global E_N_AVG

    diff_up = diff_sell = 1
    if g_market_info["price_crr_walk"] > 0:
        g_market_info["walk_up_avg"] = E(g_market_info["walk_up_avg"], g_market_info["price_crr_walk"], E_N_AVG)
        g_market_info["walk_up"] += g_market_info["price_crr_walk"]
    elif g_market_info["price_crr_walk"] < 0:
        g_market_info["walk_sell_avg"] = E(g_market_info["walk_sell_avg"], abs(g_market_info["price_crr_walk"]), E_N_AVG)
        g_market_info["walk_sell"] += abs(g_market_info["price_crr_walk"])

    if g_market_info["price_walk"] > 0 and g_market_info["walk_up"] > 0:
        g_market_info["price_walk_per"] = g_market_info["price_walk"] * 1.0 / g_market_info["walk_up"]
        diff_up = 1 - g_market_info["price_walk_per"]
    elif g_market_info["price_walk"] < 0 and g_market_info["walk_sell"] > 0:
        g_market_info["price_walk_per"] = abs(g_market_info["price_walk"]) * 1.0 / g_market_info["walk_sell"]
        diff_sell = 1 - g_market_info["price_walk_per"]
    g_market_info["walk_diff"] = diff_up * g_market_info["walk_up"] - diff_sell * g_market_info["walk_sell"] 
    
    g_market_info["walk_avg_diff"] = g_market_info["walk_up_avg"] - g_market_info["walk_sell_avg"]
    
    g_market_info["walk_all"] += abs(g_market_info["price_crr_walk"])
    return

def mkVolInfo(price_info):
    global g_market_info, g_price_info_prev
    global E_N_AVG
    
    diff_up = diff_sell = 1
    vol = price_info[4]
    vol_up = price_info[10]
    vol_sell = price_info[11]
    up_sell = vol_up - vol_sell
    sell_up = vol_sell - vol_up    
    decreaseIndex([
        "vol_up_strong_win",
        "vol_up_strong_lose",
        "vol_up_ct",
        "vol_up_shoot",
        "vol_up_weak_win",
        "vol_up_weak_lose",
#        "vol_up",
        
        "vol_sell_strong_win",
        "vol_sell_strong_lose",
        "vol_sell_ct",
        "vol_sell_shoot",
        "vol_sell_weak_win",
        "vol_sell_weak_lose",
#        "vol_sell",
    ])
    if vol_up > g_market_info["vol_up_avg"]:
        if up_sell > 0:
            g_market_info["vol_up_strong_win"] += up_sell
        else:
            g_market_info["vol_up_strong_lose"] += up_sell
            
        if g_price_info_prev and g_price_info_prev[10] < g_market_info["vol_up_avg"]:
            g_market_info["vol_up_ct"] += 1

        if vol_sell < g_market_info["vol_sell_avg"] and up_sell > 0:
            g_market_info["vol_up_shoot"] += 1
    else:
        if up_sell > 0:
            g_market_info["vol_up_weak_win"] += up_sell
        else:
            g_market_info["vol_up_weak_lose"] += up_sell
        
    g_market_info["vol_up"] += vol_up
    g_market_info["vol_up_avg"] = E(g_market_info["vol_up_avg"], vol_up, E_N_AVG)
    
    if vol_sell > g_market_info["vol_sell_avg"]:
        if sell_up > 0:
            g_market_info["vol_sell_strong_win"] += sell_up
        else:
            g_market_info["vol_sell_strong_lose"] += sell_up
            
        if g_price_info_prev and g_price_info_prev[11] < g_market_info["vol_sell_avg"]:
            g_market_info["vol_sell_ct"] += 1
            
        if vol_up < g_market_info['vol_up_avg'] and sell_up > 0:
            g_market_info["vol_sell_shoot"] += 1
    else:
        if sell_up > 0:
            g_market_info["vol_sell_weak_win"] += sell_up
        else:
            g_market_info["vol_sell_weak_lose"] += sell_up

    g_market_info["vol_sell"] += vol_sell
    g_market_info["vol_sell_avg"] = E(g_market_info["vol_sell_avg"], vol_sell, E_N_AVG)
    
#    print g_market_info["vol_up_shoot"], g_market_info["vol_sell_shoot"]
#    print g_market_info["vol_up_ct"], g_market_info["vol_sell_ct"],
#    print g_market_info["vol_up_strong_win"], g_market_info["vol_sell_strong_win"],
#    print g_market_info["vol_up_weak_win"], g_market_info["vol_sell_weak_win"],
#    print g_market_info["vol_up_strong_lose"], g_market_info["vol_sell_strong_lose"],
#    print g_market_info["vol_up_weak_lose"], g_market_info["vol_sell_weak_lose"]

    if g_market_info["price_walk"] > 0:
        diff_up = 1 - g_market_info["price_walk_per"]
    elif g_market_info["price_walk"] < 0:
        diff_sell = 1 - g_market_info["price_walk_per"]
    g_market_info["vol_diff"] = diff_up * g_market_info["vol_up"] - diff_sell * g_market_info["vol_sell"] 
#    g_market_info["vol_diff"] = g_market_info["vol_up"] - g_market_info["vol_sell"] 
    
    g_market_info["vol_avg_diff"] = g_market_info["vol_up_avg"] - g_market_info["vol_sell_avg"]
    
    g_market_info["vol_all"] += vol
    return

def mkPerInfo():
    global g_market_info
    if g_market_info["vol_all"] > 0:
        g_market_info["per_all"] = g_market_info["walk_all"] * 1.0 / g_market_info["vol_all"] * 1000
    if g_market_info["vol_up"] > 0:
        g_market_info["per_up"] = g_market_info["walk_up"] * 1.0 / g_market_info["vol_up"] * 1000
    if g_market_info["vol_sell"] > 0:
        g_market_info["per_sell"] = g_market_info["walk_sell"] * 1.0 / g_market_info["vol_sell"] * 1000

    g_market_info["per_upsell"] = g_market_info["per_up"] - g_market_info["per_sell"]
    return

def diffMarket(prev_info, crr_info):
    res = {}
    for k in crr_info.keys():
        if k == "dt":
            res[k] = crr_info[k]
        else:
            res[k] = crr_info[k] - prev_info[k]
    return res

def E(prev_num, crr_num, e_n):
    a = 2.0 / (1 + e_n)
    ret = crr_num * a + prev_num * (1 - a)
    return ret

def decreaseIndex(keys):
    global g_market_info
    global E_N_DEC
    for one in keys:
        g_market_info[one] = decreaseAdd(g_market_info[one], 0, E_N_DEC)
    return

def decreaseAdd(prev_num, crr_num, e_n):
    a = 2.0 / (1 + e_n)
    ret = crr_num + prev_num * (1 - a)
    return ret

def calcStatus(price_info):
    global g_market_info, g_market_info_prev, g_market_info_diff
    global g_market_info_e, g_market_info_e_prev, g_market_info_e_diff
    global g_price_info_prev
    
    mkPriceInfo(price_info)
    mkWalkInfo()
    mkVolInfo(price_info)
    mkPerInfo()
    mkElseInfo()
    res = {
        "info": g_market_info,
        "prev": g_market_info_prev,
        "diff": g_market_info_diff,
        "e": g_market_info_e,
        "e_prev": g_market_info_e_prev,
        "e_diff": g_market_info_e_diff,
    }
    g_price_info_prev = price_info
    return res

def listen(price_info):
    res = {}
    res = calcStatus(price_info)
    return res

if __name__ == "__main__":
    print "Hello World";
