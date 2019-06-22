#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-8 20:47:57$
# Note: This source file is NOT a freeware
# Version: ClassMarket.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-8 20:47:57$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from ClassPool import *

class MarketData(object):
    # base_info
    dt = ""
    price_info_prev = False
    count = 0
    crr = []
    # price info
    price_o = 0#
    price_h = 0#
    price_l = 10000#
    price_c = 0#
    price_h_index = 0
    price_l_index = 0
    price_up_ct = 0#
    price_sell_ct = 0#
    price_crr_walk = 0# current walk
    price_per = 0# walk / (high - low)
    price_walk = 0# total walk in pool
    price_walk_per = 0# price_walk / walk_total_direction
    # walk info
    walk_up = 0#
    walk_sell = 0#
    walk_up_avg = 0#
    walk_sell_avg = 0#
    walk_all = 0#
    # vol info
    vol_up = 0#
    vol_sell = 0#
    vol_up_avg = 0#
    vol_up_ct = 0
    vol_up_shoot = 0
    vol_up_strong_win = 0# strong win
    vol_up_strong_lose = 0# strong lose
    vol_up_weak_win = 0#weak_win
    vol_up_weak_lose = 0#weak_lose
    vol_sell_avg = 0#
    vol_sell_ct = 0
    vol_sell_shoot = 0
    vol_sell_strong_win = 0
    vol_sell_strong_lose = 0
    vol_sell_weak_win = 0
    vol_sell_weak_lose = 0
    vol_all = 0#
    # per info
    per = 0#
    per_all = 0#
    per_up = 0#
    per_sell = 0#
    per_upsell = 0#
    
    #prev
    per_all_prev = vol_all_prev = walk_all_prev = 0
    
    def __init__(self, with_prev = True):
        self.dt = ""
        self.price_info_prev = False
        self.count = 0
        self.crr = []
        
        self.price_o = self.price_h = self.price_c = self.price_h_index = self.price_l_index = self.price_up_ct = self.price_sell_ct = self.price_crr_walk = self.price_per = self.price_walk = self.price_walk_per = 0
        self.price_l = 10000
        
        self.walk_up = self.walk_sell = self.walk_up_avg = self.walk_sell_avg = self.walk_all = 0
        
        self.vol_up = self.vol_sell = self.vol_up_avg = self.vol_up_ct = self.vol_up_shoot = self.vol_up_strong_win = self.vol_up_strong_lose = self.vol_up_weak_win = self.vol_up_weak_lose = self.vol_sell_avg = self.vol_sell_ct = self.vol_sell_shoot = self.vol_sell_strong_win = self.vol_sell_strong_lose = self.vol_sell_weak_win = self.vol_sell_weak_lose = self.vol_all = 0
        
        self.per = self.per_all = self.per_up = self.per_sell = self.per_upsell = 0
        
        if with_prev:
            self.per_all_prev = self.vol_all_prev = self.walk_all_prev = 0
        return
    
    def vec(self):
#        print self.walk_all_prev, self.vol_all_prev, self.per_all_prev
        res = {
            "date": self.dt,
            "crr": self.crr[2:],
            "price": [
#                self.per_all, 
                self.price_walk, 
                self.price_up_ct, self.price_sell_ct, 
                self.price_per, self.price_h_index, self.price_l_index,
            ],
            "walk": [
                self.walk_all - self.walk_all_prev, 
                self.walk_up, self.walk_up_avg, self.walk_sell,
                self.walk_sell_avg, self.price_walk_per, self.walk_all, 
            ],
            "vol": [
                self.vol_all - self.vol_all_prev,
                self.vol_up, self.vol_up_avg, self.vol_sell,
                self.vol_sell_avg, self.vol_all,
                
                self.vol_up_strong_win, self.vol_up_strong_lose,self.vol_up_ct, 
                self.vol_up_shoot, self.vol_up_weak_win, self.vol_up_weak_lose, 
                
                self.vol_sell_strong_win, self.vol_sell_strong_lose,self.vol_sell_ct, 
                self.vol_sell_shoot, self.vol_sell_weak_win, self.vol_sell_weak_lose, 
                
                self.vol_diff, self.vol_avg_diff, 
            ],
            "per": [
                self.per_all - self.per_all_prev,
                self.per,  self.per_all, self.per_up, self.per_sell, self.per_upsell
            ]
        }
        self.per_all_prev = self.per_all
        self.vol_all_prev = self.vol_all
        self.walk_all_prev = self.walk_all
#        print self.walk_all_prev, self.vol_all_prev, self.per_all_prev
        return res
        
    def infoMkOne(self, one):
        if one:
            self.dt = one[0] + " " + one[1]
            self.crr = one
            self.count += 1
            self.mkPriceInfo(one)
            self.mkWalkInfo(one)
            self.mkVolInfo(one)
            self.price_info_prev = one
            
    def infoMk(self, datas):
        if datas:
            self.dt = datas[0][0] + " " + datas[0][1]
        else:
            return
        for one in datas:
            self.crr = one
            self.count += 1
            self.mkPriceInfo(one)
            self.mkWalkInfo(one)
            self.mkVolInfo(one)
            self.mkPer(one)
            self.price_info_prev = one
            
    def mkPriceInfo(self, one):
        if self.price_o == 0:
            self.price_o =  one[9]
        self.price_c = one[5]
        if one[6] > self.price_h:
            self.price_h = one[6]
            self.price_h_index = self.count
        elif one[7] < self.price_l:
            self.price_l = one[7]
            self.price_l_index = self.count

        self.price_crr_walk = one[3]
        if one[3] > 0:
            self.price_up_ct += 1
        elif one[3] < 0:
            self.price_sell_ct += 1

        self.price_walk = self.price_c - self.price_o
        self.price_per = self.price_walk * 100.0 / (self.price_h - self.price_l)

    def mkWalkInfo(self, one):
        hl_diff = one[6] - one[7] - abs(one[3])
#        hl_diff = 0
        if hl_diff < 0:
            hl_diff = 0
        self.walk_up += hl_diff
        self.walk_sell += hl_diff
        if self.price_crr_walk > 0:
            self.walk_up += self.price_crr_walk
            if self.price_up_ct > 0:
                self.walk_up_avg = self.walk_up / self.price_up_ct
        elif self.price_crr_walk < 0:
            self.walk_sell += abs(self.price_crr_walk)
            if self.price_sell_ct > 0:
                self.walk_sell_avg = self.walk_sell / self.price_sell_ct

        if self.price_walk > 0 and self.walk_up > 0:
            self.price_walk_per = self.price_walk * 1.0 / self.walk_up
        elif self.price_walk < 0 and self.walk_sell > 0:
            self.price_walk_per = abs(self.price_walk) * 1.0 / self.walk_sell

        self.walk_all += abs(self.price_crr_walk) + hl_diff*2

    def mkVolInfo(self, price_info):
        diff_up = diff_sell = 1
        vol = price_info[4]
        vol_up = price_info[10]
        vol_sell = price_info[11]
        up_sell = vol_up - vol_sell
        sell_up = vol_sell - vol_up  
        
        self.vol_up += vol_up
        self.vol_up_avg = self.vol_up / self.count
        self.vol_sell += vol_sell
        self.vol_sell_avg = self.vol_sell / self.count

        if vol_up > self.vol_up_avg:
            if up_sell > 0:
                self.vol_up_strong_win += up_sell
            else:
                self.vol_up_strong_lose += up_sell

            if self.price_info_prev and self.price_info_prev[10] < self.vol_up_avg:
                self.vol_up_ct += 1

            if vol_sell < self.vol_sell_avg and up_sell > 0:
                self.vol_up_shoot += 1
        else:
            if up_sell > 0:
                self.vol_up_weak_win += up_sell
            else:
                self.vol_up_weak_lose += up_sell

        if vol_sell > self.vol_sell_avg:
            if sell_up > 0:
                self.vol_sell_strong_win += sell_up
            else:
                self.vol_sell_strong_lose += sell_up

            if self.price_info_prev and self.price_info_prev[11] < self.vol_sell_avg:
                self.vol_sell_ct += 1

            if vol_up < self.vol_up_avg and sell_up > 0:
                self.vol_sell_shoot += 1
        else:
            if sell_up > 0:
                self.vol_sell_weak_win += sell_up
            else:
                self.vol_sell_weak_lose += sell_up

        if self.price_walk > 0:
            diff_up = 1 - self.price_walk_per
        elif self.price_walk < 0:
            diff_sell = 1 - self.price_walk_per
        self.vol_diff = diff_up * self.vol_up - diff_sell * self.vol_sell 

        self.vol_avg_diff = self.vol_up_avg - self.vol_sell_avg
        self.vol_all += vol
    
    def mkPer(self, one):
        self.per = self.price_walk / self.vol_all
        direction = 0
        if self.price_walk != 0:
            direction = self.price_walk / abs(self.price_walk)
        self.per_all = self.walk_all / self.vol_all# * direction
        if self.vol_up:
            self.per_up = self.walk_up / self.vol_up
        if self.vol_sell:
            self.per_sell = self.walk_sell / self.vol_sell
        self.per_upsell = self.per_up - self.per_sell
    
class Market(object):
    info = False
    pool = False
    len = 0
    def __init__(self, length, type="time"):
        self.len = length
        self.type = type
        self.reInit()
    
    def reInit(self):
        self.info = MarketData()
#        print self.type
        if self.type == "vol":
#            print "vol"
            self.pool = PoolVol(self.len)
        else:
#            print "time"
            self.pool = Pool(self.len)
        
    def add(self, one):
        self.pool.add(one)
    
    def get(self, clean_pool = False):
        res = False
        if self.pool.reach_max:
            res = self.calc()
            self.info.__init__(False);

            if clean_pool:
                self.pool.clean()
        return res
    
    def calcSet(self, datas):
        self.info.__init__(False);
        self.info.infoMk(datas)
        return self.info.vec()
    
    def calc(self):
        self.mkMarket()
        return self.info.vec()
    
    def mkMarket(self):
        data = self.pool.getData()
        self.info.infoMk(data)    
    
if __name__ == "__main__":
    print "Hello World";
