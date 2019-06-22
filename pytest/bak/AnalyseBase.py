#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-3-29 20:47:44$
# Note: This source file is NOT a freeware
# Version: AnalyseBase.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-3-29 20:47:44$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

g_pool_info_ls = []
g_crr_direction = 0
def poolSig(pool_info):
    global g_pool_info_ls, g_crr_direction
    sig = 0
    tmp1 = pool_info["walk"] * pool_info["all_per"] # none use
    tmp2 = pool_info["walk"] * pool_info["one_per"]
    tmp3 = pool_info["walk"] * pool_info["updown_per"]
    tmp4 = pool_info["walk"] * pool_info["updown_walk"]
    tmp5 = pool_info["walk"] * pool_info["updown_vol"]
    tmp6 = pool_info["walk"] * pool_info["updown_price"]
    tmp7 = pool_info["walk"] * pool_info["price_e"]
#    if tmp1 > 0 and tmp2 > 0 and tmp3 > 0 and tmp4 > 0 and tmp5 > 0 and tmp6 > 0 and tmp7 > 0:
    if tmp5 > 0 and tmp3 > 0 and tmp6 > 0:
#    if tmp5 > 0:
#    if pool_info["updown_per"] * pool_info["updown_vol"] > 0:
        sig = pool_info["walk"] / abs(pool_info["walk"])
        g_crr_direction = sig
#    if pool_info["one_per"] != 0: # only for test
#        sig = pool_info["one_per"] / abs(pool_info["one_per"])
    g_pool_info_ls.append(pool_info)
    return sig

def getCrrDirection():
    global g_crr_direction
    return g_crr_direction

def poolInfo(pool):
    res = {}
 
    dt = ""
    open_p = pool[0][9]
    close_p = 0
    high_p = 0
    low_p = 10000
    walk_all = 0
    vol_all = 0
    pool_len = len(pool)
    per_up = per_down = 0
    walk_up = walk_down = 0
    vol_up = vol_down = 0
    price_up = price_down = 0 # means times
    price_e_up = price_e_down = 0
    
    for one in pool:
        dt = one[0] + " " + one[1]
        if one[6] > high_p:
            high_p = one[6]
        if one[7] < low_p:
            low_p = one[7]
        close_p = one[5]
        vol_all += one[4]
        
        if one[3] > 0:
            per_up += one[2]
            walk_up += one[3]
            vol_up += one[4]
            price_up += 1
            price_e_up += one[8]
        elif one[3] < 0:
            per_down += abs(one[2])
            walk_down += abs(one[3])
            vol_down += one[4]
            price_down += 1
            price_e_down += abs(one[8])
            
    walk_all = all_per = walk_p = 0
    walk_all = round(close_p - open_p, 2)
#    if vol_all > 0:
#        all_per = round((walk_all / vol_all) * 1000, 5)
#    else:
#        all_per = 0
    if walk_all > 0 and walk_up > 0:
        walk_p = walk_all * 1.0 / walk_up
    elif walk_all < 0 and walk_down > 0:
        walk_p = abs(walk_all) * 1.0 / walk_down
    
    one_per = updown_per = updown_walk = updown_vol = updown_price = price_e = 0
    vol_walk = vol_p = 0
    diff_up = diff_down = 1
    diff_p = 1 - walk_p
    if walk_all > 0:
        diff_up = diff_p
        vol_walk = int(vol_up * walk_p)
    elif walk_all < 0:
        diff_down = diff_p
        vol_walk = int(vol_down * walk_p)
    one_per = round((per_up - per_down) / pool_len, 5)
    updown_walk = round(walk_up * diff_up - walk_down * diff_down, 2)
    updown_vol = int(vol_up * diff_up - vol_down * diff_down)
    updown_price = price_up - price_down
    price_e = round(price_e_up * diff_up - price_e_down * diff_down, 2)
        
    vol_p = round(vol_walk/vol_all, 3)
    if vol_walk:
        all_per = round(walk_all / vol_walk * 1000, 5)
    if vol_up != 0 and vol_down != 0:
        updown_per = round((walk_up/vol_up - walk_down/vol_down) * 1000, 5)
    else:
        updown_per = 0
    
    res = {
        "date": dt, "time": "",  "walk": walk_all,
        "walk_p": round(walk_p*100,2), "vol": vol_all, "vol_p": vol_p,
        "vol_walk": vol_walk, "open": open_p, "high": high_p,
        "low": low_p, "close": close_p, "all_per": all_per,
        "one_per": one_per, "updown_per": updown_per, "updown_walk": updown_walk,
        "updown_vol": updown_vol, "updown_price": updown_price, "price_e": price_e,
    }
    return res.copy()

def poolInfoBack(pool):
    res = {}
 
    per = 0
    walk_all = 0
    walk_up = 0
    walk_down = 0
    vol_all = 0
    vol_up = 0
    vol_down = 0
    price_updown = 0
    high_p = 0
    low_p = 10000
    close_p = 0
    price_e = 0
    dt = ""
    open_p = pool[0][9]
    pool_len = len(pool)
    
    for one in pool:
        dt = one[0] + " " + one[1]
        per += one[2] / pool_len
        price_e += one[8]
        price_updown += one[3] / abs(one[3])
        walk_all += one[3]
        vol_all += one[4]
        close_p = one[5]
        if one[6] > high_p:
            high_p = one[6]
        if one[7] < low_p:
            low_p = one[7]
        if one[3] > 0:
            walk_up += one[3]
            vol_up += one[4]
        elif one[3] < 0:
            walk_down += abs(one[3])
            vol_down += one[4]
    walk_all = close_p - open_p
    if vol_up != 0 and vol_down != 0:
        up_down_per = walk_up/vol_up - walk_down/vol_down
    else:
        up_down_per = 0
    if vol_all > 0:
        all_per = walk_all / vol_all
    else:
        all_per = 0
    walkupdown = walk_up - walk_down
    volupdown = vol_up - vol_down
    walk_per = 0
    vol_walk = 0
    if walk_all > 0:
        walk_per = round(walk_all * 100 / walk_up, 2)
        vol_walk = int(vol_up * walk_per / 100)
        volupdown -= vol_walk
    else:
        walk_per = round(abs(walk_all) * 100 / walk_down, 2)
        vol_walk = int(vol_down * walk_per / 100)
        volupdown += vol_walk
    res = {
        "date": dt,
        "time": "",
        "walk": walk_all,
        "walk_p": walk_per,
        "vol": vol_all,
        "vol_p": round(vol_walk/vol_all, 3),
        "vol_walk": vol_walk,
        "open": open_p,
        "high": high_p,
        "low": low_p,
        "close": close_p,
        "all_per": all_per,
        "one_per": per,
        "updown_per": up_down_per,
        "updown_walk": walkupdown,
        "updown_vol": volupdown,
        "updown_price": price_updown,
        "price_e": price_e,
    }
    return res.copy()

if __name__ == "__main__":
    print "Hello World";
