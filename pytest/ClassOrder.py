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

class Order(object):
    history = []
    result = []
    win_count = 0
    count = 0
    up_win = 0
    up_lose = 0
    sell_win = 0
    sell_lose = 0
    profit_sum = 0
    lose_max = 0
    win_max = 0
    lose_avg = 0
    win_avg = 0
    tick_sum = 0
    deal = {}
    stop_chg = True
    stop_lose = 1000
    
    def __init__(self, stop_chg = True, stop_lose = 1000):
        self.stop_chg = stop_chg
        self.stop_lose = stop_lose
        self.deal = {
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
    
    def tick(self, high_p, low_p, crr_p):
        global OP_UP, OP_SELL
        global STOP_T_LOSE, STOP_T_WIN, STOP_CHG_MIN
        ret = {}
        profit = 0
        if self.deal["is_open"] == True:
            self.deal["tick"] += 1
            if self.deal['high_price'] < crr_p:
                self.deal['high_price'] = crr_p
                self.deal['high_tick'] = self.deal["tick"]
            if self.deal['low_price'] > crr_p:
                self.deal['low_price'] = crr_p
                self.deal['low_tick'] = self.deal["tick"]
            profit = self.profit(self.deal, crr_p)
            if self.deal['direction'] == OP_UP:
                if self.deal["stop_lose"] != 0 and self.deal["stop_lose"] > low_p: # who first? --TODO
                    ret = self.close("", self.deal["stop_lose"], STOP_T_LOSE)
                if self.deal["stop_win"] != 0 and self.deal["stop_win"] < high_p:
                    ret = self.close("", self.deal["stop_win"], STOP_T_WIN)
            elif self.deal['direction'] == OP_SELL:
                if self.deal["stop_lose"] != 0 and self.deal["stop_lose"] < high_p: # who first? --TODO
                    ret = self.close("", self.deal["stop_lose"], STOP_T_LOSE)
                if self.deal["stop_win"] != 0 and self.deal["stop_win"] > low_p:
                    ret = self.close("", self.deal["stop_win"], STOP_T_WIN)
                    
            if self.stop_chg and not ret and profit > STOP_CHG_MIN and (crr_p - self.deal["stop_lose"])* self.deal['direction'] > self.stop_lose :
                self.deal["stop_lose"] = crr_p - self.stop_lose * self.deal['direction']
        return ret
    
    def profit(self, deal, price):
        if deal:
            return (price - deal["open_price"]) * deal["direction"]
        return 0
    
    def open(self, tm, opt, price, stop_lose, stop_win):
        if self.deal["is_open"] == True:
            # already open
            return False

        self.deal["open_time"] = tm
        self.deal["close_time"] = 0
        self.deal["direction"] = opt
        self.deal['open_price'] = price
        self.deal["stop_lose"] = stop_lose
        self.deal["stop_win"] = stop_win
        self.deal["stop_type"] = 0
        self.deal["close_price"] = 0
        self.deal["profit"] = 0
        self.deal["is_open"] = True
        self.deal["tick"] = 1
        self.deal['high_price'] = self.deal['low_price'] = price
        self.deal['high_tick'] = self.deal['low_tick'] = 1
        return self.deal.copy()

    def close(self, tm, price, t):
        global OP_UP, OP_SELL

        if self.deal["is_open"] == False:
            # already close
            return False
        profit = self.profit(self.deal, price)
        self.deal["close_time"] = tm
        self.deal["close_price"] = price
        self.deal["is_open"] = False
        self.deal["stop_type"] = t
        self.deal["profit"] = profit
        self.count += 1
        self.profit_sum += profit
        self.tick_sum += self.deal["tick"]
        if profit < self.lose_max:
            self.lose_max = profit
        if profit > self.win_max:
            self.win_max = profit
        self.history.append(self.deal.copy())
        if profit > 0:
            self.win_avg = (self.win_avg * self.win_count + profit) / (self.win_count+1)
            self.win_count += 1
            if self.deal['direction'] == OP_UP:
                self.up_win += 1
            elif self.deal['direction'] == OP_SELL:
                self.sell_win += 1
        elif profit < 0:
            self.lose_avg = (self.lose_avg * (self.up_lose+self.sell_lose) + profit) / (self.up_lose+self.sell_lose+1)
            if self.deal['direction'] == OP_UP:
                self.up_lose += 1
            elif self.deal['direction'] == OP_SELL:
                self.sell_lose += 1
        #    print "order close: ", self.deal, profit
        self.result.append([
            self.deal['open_time'], self.deal['open_price'], self.deal['high_price'], self.deal['low_price'], 
            int((self.deal["high_tick"] - self.deal['low_tick']) * self.deal['direction'] < 0), 
            self.deal["tick"], self.deal['direction'], profit, self.profit_sum 
            ])
        return self.deal.copy()
        
    def info(self):
        if not self.count:
            if self.dealOpen():
                print "deal: ", self.deal['direction']
            else:
                print "no deals"
            return
        print "winper: ", self.win_count * 100.0 / self.count
        print "total: ", self.count
        print "detail: ", self.up_win, self.up_lose, self.sell_win, self.sell_lose
        print "profit: ", self.profit_sum
        print "win_max: ", self.win_max
        print "lose_max: ", self.lose_max
        print "win_avg: ", self.win_avg
        print "lose_avg: ", self.lose_avg
        print "tick_avg", self.tick_sum / len(self.history)
        return self.result

    def dealOpen(self):
        if self.deal["is_open"] == True:
            return True
        return False
    
if __name__ == "__main__":
    print "Hello World";
