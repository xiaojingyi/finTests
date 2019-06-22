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
stop_lose = -50
stop_win = 50
stop_len = 50
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
#            print "no data"
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
#        print "walk 0"
        return
#        walk_per = price_walk*price_walk*price_walk/abs(price_walk) / vol * 1000
    walk_per = price_walk / vol * 1000
#    avg_price = (open_p + close_p) / 2
    avg_price = close_p
    mini_line = [one[0], one[1], walk_per, price_walk, vol, avg_price, high_p, low_p]
    return mini_line

opt_ct = 0
def sendOrder(sig):    
    global opt_ct
    
    if sig == "0" or sig == False:
        print opt_ct, sig
        return
    
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
            print "send sig loop: ", sig
            time.sleep(0.2)
#            print is_stop
        if is_stop == 1:
            break
    return

def main():
    import Analyse
    mini_line = []
    while(1):
        one = mkMiniLine()
        if not one:
#            print "no one"
            continue
        
        if one and mini_line and mini_line[0] == one[0]:
#            print "if one and mini_line and mini_line[0] == one[0]"
            time.sleep(sleep_set)
            continue
        
        mini_line = one
        
        Analyse.addData(mini_line)
        res = Analyse.calcPool()
#        print res
        if res:
            opt = Analyse.addDeal(res)
            if opt:
                for one_opt in opt:
                    print mini_line[0],
                    sendOrder(one_opt)
            
        time.sleep(sleep_set)
    print "done res file"
    
if __name__ == "__main__":
    main()