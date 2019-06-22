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
from ClassDataSrc import *
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

#global_source_file = "data/XAUUSD1-hst-new.csv"
#global_source_file = "data/XAUUSD1.csv"
global_source_file = "data/XAUUSD60.csv"
#global_source_file = "data/tick_IF_all.csv"
#global_source_file = "data/tick_IF/20150311_IF.csv"
res_file = "server_test_res.csv"

def openDeal(order, signar, one):
    global stop_lose, stop_win
    
    price = one[5]
    date_info = one[0] + " " + one[1]
    if signar > 0:
        if order.dealOpen() and order.deal["direction"] == OP_SELL:
            order.close(date_info, price, STOP_T_CMD)
        order.open(date_info, OP_UP, price, price-stop_lose, price+stop_win)
    elif signar < 0:
        if order.dealOpen() and order.deal["direction"] == OP_UP:
            order.close(date_info, price, STOP_T_CMD)
        order.open(date_info, OP_SELL, price, price+stop_lose, price-stop_win)
    return

def main():
    global test_result, global_give_opside, global_price_chg_min
    global stop_win, stop_lose
    import Analyse_price_walk as Analyse
    from ClassLine import Line
    from ClassMarket import Market
    from ClassPredict import Predict
    
    p = Predict(2, 2000)
    order = Order(True, stop_lose)
    
    dsrc = DataSrc(global_source_file)
 
    last_vec = []
    last_info = []
    correct_ct = ct = i = 0
    walk_p = 0
    date_info = ""
    price = 0
    price_use = 0
    while(1):
        i += 1
        one = dsrc.getLine()
        if not one:
            break
        walk = one[3]
        price = one[5]
#        print price_use, walk_use
        date_info = one[0] + " " + one[1] 
        
        order.tick(one[6], one[7], price)
        
        res = p.predict(walk)
        next_e = res[2]
        if abs(next_e) > 0:
            openDeal(order, next_e, one)

        if i % 50 == 0:
            order.info()
            print "-------------------------"

    order.close(date_info, price, STOP_T_CMD)
    res = order.info()
    dsrc.done()
    if res:
        mkCsvFileWin("test_deals_info.csv", res)
    print "done"

if __name__ == "__main__":
    main()
    