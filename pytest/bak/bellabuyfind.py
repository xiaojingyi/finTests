#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-15 17:05:25$
# Note: This source file is NOT a freeware
# Version: bellabuyfind.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-15 17:05:25$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from lib.Util import *
import re

file_dir = "D:/documents/projects/跨境电商/项目文档/04.过渡/代码/ios/Qugo/trunk/BellaBuy"
def findLine(line):
    res = ""
    if line.find("showWithCustomAlertViewWithText:@\"") > 0:
        res =  line
    if line.find("setTitle:@\"") > 0:
        res =  line
    if line.find("setText:@\"") > 0:
        res =  line
    if line.find(".text = @\"") > 0:
        res =  line
    if line.find(".text =@\"") > 0:
        res =  line
    if line.find(".text= @\"") > 0:
        res =  line
    if line.find(".text=@\"") > 0:
        res =  line
    if not res:
        return False
    strs = False
    try:
        strs = re.search(r'\"([^"]+)\"',res).groups()[0]
    except:
        strs = False
    return strs

def findLines(fname):
    fname_class = fname.split("\\")[-1]
    data = readFileLines(fname)
    lines = []
    for one in data:
        l = findLine(one)
        if l:
            tmp = [fname_class, l]
            if tmp not in lines:
                lines.append(tmp)
    return lines

def main():
    ls = walkDir(file_dir)
    res = []
    for one in ls:
        if one[-2:] == ".m":
            tmp = findLines(one)
            res.extend(tmp)
    
    mkCsvFileWin("texts.csv", res)

if __name__ == "__main__":
    print
