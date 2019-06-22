#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-4 17:53:17$
# Note: This source file is NOT a freeware
# Version: if_mkbig.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-4 17:53:17$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
from lib.Util import * 

if __name__ == "__main__":
    ls = walkDir("data/tick_IF")
    ls.sort()
    file_w = open("data/tick_IF_all.csv", "w")
    for one in ls:
        print one
        data = getFileContent(one)
        file_w.write(data)
    file_w.close()
