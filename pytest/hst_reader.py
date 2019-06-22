#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-3-28 14:45:53$
# Note: This source file is NOT a freeware
# Version: hst_reader.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-3-28 14:45:53$"

import os, sys, time, struct
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from lib.Util import *

def fileInfo(file):
    ver = struct.unpack("l",file.read(4))[0]
    print "version: ", ver
    copyright = file.read(64)#struct.unpack("s",file.read(1))
    print "copyright: ", copyright
    symbol = file.read(12)
    print "symbol: ", symbol
    period = struct.unpack("l",file.read(4))[0]
    print "period: ", period
    digits = struct.unpack("l",file.read(4))[0]
    print "digits: ", digits
    timesign = struct.unpack("l",file.read(4))[0]
    print "timesign: ", timesign
    last_sync = struct.unpack("l",file.read(4))[0]
    print "last_sync: ", last_sync
    unused = file.read(52)
    print "unused: ", unused
    
    return 

def onedata(file):
    fist_r = file.read(8)
    if not fist_r:
        return False
    ctm = struct.unpack("q",fist_r)[0]
    ctm = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ctm))
    ctm = ctm.split(" ")
    p_open = struct.unpack("d",file.read(8))[0]
    p_high = struct.unpack("d",file.read(8))[0]
    p_low = struct.unpack("d",file.read(8))[0]
    p_close = struct.unpack("d",file.read(8))[0]
    vol = struct.unpack("q",file.read(8))[0]
    spread = struct.unpack("l",file.read(4))[0]
    real_vol = struct.unpack("q",file.read(8))[0]
    
    info_str = str(ctm[0]) + ", " + str(ctm[1]) + ", " + str(p_open) + ", " + str(p_high) + ", " + str(p_low) + ", " + str(p_close) + ", " + str(vol) + ", " + str(spread) + ", " + str(real_vol) + "\n"
#    print info_str
    return info_str
    return [ctm, p_open, p_high, p_low, p_close, vol, spread, real_vol]

if __name__ == "__main__":
    file = open('data/XAUUSD1.hst','rb')
    fileInfo(file)
    res = ""
    i = 0
    file_w = open("data/XAUUSD1-hst.csv", "w")
    while(1):
        data = onedata(file)
        if not data:
            break
        res += data
#        print data
        i += 1
        if i % 8000 == 0:
            file_w.write(res)
            res = ""
            print "finished: ", i
    print "done read, start make csv..."
    file.close()
    file_w.write(res)
    file_w.close()
    print "Hello World";
